import json
import logging
import threading
import time
from typing import Any, Dict, Optional, Callable, List
from uuid import UUID
import asyncio
from threading import Lock
import collections

from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError, NoBrokersAvailable
from fastapi import WebSocket
from starlette.websockets import WebSocketState
from app.exceptions.custom_error import CustomError

class KafkaService:
    def __init__(self, bootstrap_servers=None):
        self.bootstrap_servers = bootstrap_servers or 'kafka:9092'  # Default to container hostname instead of localhost
        self.producer = None
        self.active_connections: Dict[str, WebSocket] = {}
        self.connections_lock = Lock()  # Add lock for thread safety
        self._logger = logging.getLogger(__name__)
        self._notification_consumer_thread = None
        self._notification_consumer_running = False
        self._consumers = {}  # Store consumer threads
        # Add notification buffer for offline users
        self.notification_buffer: Dict[str, collections.deque] = {}
        self.notification_buffer_lock = Lock()
        self.max_buffer_size = 50  # Store up to 50 notifications per user
        self._init_producer()
        
    def _init_producer(self):
        retry_interval = 5
        max_retry_interval = 60
        max_retries = 5
        retries = 0
        
        while retries < max_retries:
            try:
                def json_serializer(obj):
                    if isinstance(obj, UUID):
                        return str(obj)
                    raise CustomError.INTERNAL_SERVER_ERROR.as_exception()
                    
                self.producer = KafkaProducer(
                    bootstrap_servers=self.bootstrap_servers,
                    value_serializer=lambda v: json.dumps(v, default=json_serializer).encode('utf-8'),
                    request_timeout_ms=10000,  # Increase timeout for better reliability
                    retry_backoff_ms=500,
                    acks='all'  # Ensure messages are durably stored
                )
                self._logger.info(f"Kafka producer initialized successfully to {self.bootstrap_servers}")
                return
            except NoBrokersAvailable:
                self._logger.warning(f"Kafka brokers not available at {self.bootstrap_servers}, retry {retries+1}/{max_retries}")
                retries += 1
                time.sleep(retry_interval)
                retry_interval = min(retry_interval * 2, max_retry_interval)
            except Exception as e:
                self._logger.error(f"Error initializing Kafka producer: {str(e)}")
                retries += 1
                time.sleep(retry_interval)
                retry_interval = min(retry_interval * 2, max_retry_interval)
        
        self._logger.error(f"Failed to initialize Kafka producer after {max_retries} attempts")
        self.producer = None

    def _ensure_producer(self):
        if self.producer is None:
            self._init_producer()
        return self.producer is not None

    def send_message(self, topic: str, message: Dict[str, Any]):
        if not self._ensure_producer():
            self._logger.error("Cannot send message: Kafka producer not available")
            raise CustomError.SERVICE_UNAVAILABLE.as_exception()
            
        try:
            future = self.producer.send(topic, message)
            future.get(timeout=10)  # Wait for message to be sent
            self.producer.flush(timeout=5)  # Ensure message is sent
            return {"status": "success", "message": f"Message sent to {topic}"}
        except KafkaError as e:
            self._logger.error(f"Kafka error sending message: {str(e)}")
            raise CustomError.MESSAGE_DELIVERY_FAILED.as_exception()
        except Exception as e:
            self._logger.error(f"Error sending message to Kafka: {str(e)}")
            raise CustomError.INTERNAL_SERVER_ERROR.as_exception()

    async def register_connection(self, user_id: str, websocket: WebSocket):
        """Register a WebSocket connection for a user"""
        await websocket.accept()
        
        with self.connections_lock:
            self.active_connections[user_id] = websocket
        
        self._logger.info(f"WebSocket connection registered for user {user_id}")
        
        # Deliver any buffered notifications
        await self._deliver_buffered_notifications(user_id)
        
        # Start the notification consumer if not already running
        self.start_notification_consumer()

    async def _deliver_buffered_notifications(self, user_id: str):
        """Deliver any buffered notifications to the newly connected user"""
        with self.notification_buffer_lock:
            if user_id not in self.notification_buffer or not self.notification_buffer[user_id]:
                return  # No notifications to deliver
                
            buffer = self.notification_buffer[user_id]
            self._logger.info(f"Delivering {len(buffer)} buffered notifications to user {user_id}")
            
            # Get websocket
            websocket = None
            with self.connections_lock:
                if user_id in self.active_connections:
                    websocket = self.active_connections[user_id]
            
            if not websocket:
                self._logger.warning(f"Cannot deliver buffered notifications: no active connection for user {user_id}")
                return
                
            # Send all buffered notifications
            while buffer:
                try:
                    notification = buffer.popleft()
                    await websocket.send_json(notification)
                    self._logger.info(f"Delivered buffered notification to user {user_id}")
                    # Short delay to avoid overwhelming the client
                    await asyncio.sleep(0.1)
                except Exception as e:
                    self._logger.error(f"Error delivering buffered notification to user {user_id}: {str(e)}")
                    # Stop delivery if there's an error
                    break

    def _buffer_notification(self, user_id: str, notification: Dict[str, Any]):
        """Buffer a notification for a user who is currently offline"""
        with self.notification_buffer_lock:
            if user_id not in self.notification_buffer:
                self.notification_buffer[user_id] = collections.deque(maxlen=self.max_buffer_size)
                
            self.notification_buffer[user_id].append(notification)
            self._logger.info(f"Buffered notification for offline user {user_id}, buffer size: {len(self.notification_buffer[user_id])}")

    def remove_connection(self, user_id: str):
        """Remove a WebSocket connection for a user"""
        with self.connections_lock:
            if user_id in self.active_connections:
                del self.active_connections[user_id]
                self._logger.info(f"WebSocket connection removed for user {user_id}")

    async def send_notification(self, user_id: str, notification: Dict[str, Any]):
        """Send a notification to a user through WebSocket"""
        websocket = None
        
        with self.connections_lock:
            if user_id in self.active_connections:
                websocket = self.active_connections[user_id]
        
        if websocket is None:
            self._logger.warning(f"No active WebSocket connection for user {user_id}, buffering notification")
            self._buffer_notification(user_id, notification)
            return False
            
        try:
            # Check WebSocket state properly
            if websocket.client_state == WebSocketState.DISCONNECTED:
                self._logger.warning(f"WebSocket for user {user_id} is disconnected, buffering notification and removing connection")
                self._buffer_notification(user_id, notification)
                self.remove_connection(user_id)
                return False

            await websocket.send_json(notification)
            self._logger.info(f"Notification sent to user {user_id} via WebSocket")
            return True
        except RuntimeError as e:
            if "websocket operation outside of a connection" in str(e).lower():
                self._logger.warning(f"WebSocket for user {user_id} is no longer connected, buffering notification and removing connection")
                self._buffer_notification(user_id, notification)
                self.remove_connection(user_id)
            else:
                self._logger.error(f"Runtime error sending notification to user {user_id}: {str(e)}")
                self._buffer_notification(user_id, notification)
            return False
        except Exception as e:
            self._logger.error(f"Error sending notification to user {user_id}: {str(e)}")
            self._buffer_notification(user_id, notification)
            self.remove_connection(user_id)
            return False

    def start_consumer(self, topic: str, group_id: str, callback: Callable):
        consumer_key = f"{topic}:{group_id}"
        
        # Check if already running
        if consumer_key in self._consumers and self._consumers[consumer_key].is_alive():
            self._logger.info(f"Consumer for {topic} with group {group_id} is already running")
            return

        consumer_thread = threading.Thread(
            target=self._consumer_worker,
            args=(topic, group_id, callback),
            daemon=True
        )
        self._consumers[consumer_key] = consumer_thread
        consumer_thread.start()
        self._logger.info(f"Started consumer for {topic} with group {group_id}")
        
    def _consumer_worker(self, topic: str, group_id: str, callback: Callable):
        """Worker function for consumer threads"""
        retry_interval = 5
        max_retry_interval = 60
        running = True
        
        while running:
            try:
                consumer = KafkaConsumer(
                    topic,
                    bootstrap_servers=self.bootstrap_servers,
                    group_id=group_id,
                    auto_offset_reset='earliest',
                    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                    session_timeout_ms=30000,  # Increased session timeout for better stability
                    heartbeat_interval_ms=10000
                )
                
                self._logger.info(f"Kafka consumer connected to topic {topic}")
                
                # Process messages
                for message in consumer:
                    try:
                        callback(message.value)
                    except Exception as e:
                        self._logger.error(f"Error processing message: {str(e)}")
                        
            except NoBrokersAvailable:
                self._logger.warning(f"No Kafka brokers available, retrying in {retry_interval} seconds...")
                time.sleep(retry_interval)
                # Exponential backoff with a cap
                retry_interval = min(retry_interval * 2, max_retry_interval)
                
            except Exception as e:
                self._logger.error(f"Error in Kafka consumer: {str(e)}, retrying in {retry_interval} seconds...")
                time.sleep(retry_interval)
                retry_interval = min(retry_interval * 2, max_retry_interval)
    
    def start_notification_consumer(self):
        if self._notification_consumer_running:
            return
            
        self._notification_consumer_running = True
        self._notification_consumer_thread = threading.Thread(
            target=self._run_notification_consumer,
            daemon=True
        )
        self._notification_consumer_thread.start()
        self._logger.info("Notification consumer started")
        
    def stop_notification_consumer(self):
        if not self._notification_consumer_running:
            return
            
        self._notification_consumer_running = False
        if self._notification_consumer_thread:
            try:
                self._notification_consumer_thread.join(timeout=5)
                self._logger.info("Notification consumer stopped")
            except Exception as e:
                self._logger.error(f"Error stopping notification consumer: {str(e)}")
    
    def _run_notification_consumer(self):
        """Run the notification consumer that forwards Kafka messages to WebSockets"""
        def callback(message: Dict[str, Any]):
            try:
                user_id = message.get("user_id")
                notification = message.get("notification")
                
                if not user_id or not notification:
                    self._logger.error(f"Invalid notification message: {message}")
                    return

                user_id = str(user_id)
                self._logger.info(f"Received notification for user {user_id}")
                    
                # Create a new event loop for this thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Send notification to user via WebSocket
                try:
                    result = loop.run_until_complete(self.send_notification(user_id, notification))
                    if result:
                        self._logger.info(f"Successfully sent notification to user {user_id}")
                    else:
                        self._logger.warning(f"Failed to send notification to user {user_id}, notification buffered")
                finally:
                    loop.close()
                    
            except Exception as e:
                self._logger.exception(f"Error processing notification message: {str(e)}")
                
        # Start the consumer for the user_notifications topic
        self._logger.info("Starting Kafka consumer for user notifications")
        self.start_consumer("user_notifications", "notification_consumer_group", callback)
                
    def create_job_task(self, job_id: UUID, user_id: UUID, task_data: Optional[Dict] = None):
        """Create a job task in Kafka"""
        message = {
            "job_id": job_id,
            "user_id": user_id,
            "data": task_data or {}
        }
        return self.send_message("job_tasks", message) 
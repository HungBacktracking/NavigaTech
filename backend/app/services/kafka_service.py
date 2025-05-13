import json
import logging
import threading
import time
from typing import Any, Dict, Optional, Callable
from uuid import UUID
import asyncio

from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError, NoBrokersAvailable
from fastapi import WebSocket

class KafkaService:
    def __init__(self, bootstrap_servers=None):
        self.bootstrap_servers = bootstrap_servers or 'kafka:9092'  # Default to container hostname instead of localhost
        self.producer = None
        self.active_connections: Dict[str, WebSocket] = {}
        self._logger = logging.getLogger(__name__)
        self._notification_consumer_thread = None
        self._notification_consumer_running = False
        self._consumers = {}  # Store consumer threads
        self._init_producer()
        
    def _init_producer(self):
        """Initialize Kafka producer with retry logic"""
        try:
            def json_serializer(obj):
                if isinstance(obj, UUID):
                    return str(obj)
                raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
                
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v, default=json_serializer).encode('utf-8'),
                request_timeout_ms=10000,  # Increase timeout for better reliability
                retry_backoff_ms=500
            )
            self._logger.info(f"Kafka producer initialized successfully to {self.bootstrap_servers}")
        except NoBrokersAvailable:
            self._logger.warning(f"Kafka brokers not available at {self.bootstrap_servers}, will retry later")
            self.producer = None
        except Exception as e:
            self._logger.error(f"Error initializing Kafka producer: {str(e)}")
            self.producer = None

    def _ensure_producer(self):
        if self.producer is None:
            self._init_producer()
        return self.producer is not None

    def send_message(self, topic: str, message: Dict[str, Any]):
        """Send a message to a Kafka topic"""
        if not self._ensure_producer():
            self._logger.error("Cannot send message: Kafka producer not available")
            return {"status": "error", "message": "Kafka service unavailable"}
            
        try:
            future = self.producer.send(topic, message)
            future.get(timeout=10)  # Wait for message to be sent
            return {"status": "success", "message": f"Message sent to {topic}"}
        except KafkaError as e:
            self._logger.error(f"Kafka error sending message: {str(e)}")
            return {"status": "error", "message": f"Kafka error: {str(e)}"}
        except Exception as e:
            self._logger.error(f"Error sending message to Kafka: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def register_connection(self, user_id: str, websocket: WebSocket):
        """Register a WebSocket connection for a user"""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self._logger.info(f"WebSocket connection registered for user {user_id}")
        
        # Start the notification consumer if not already running
        self.start_notification_consumer()

    def remove_connection(self, user_id: str):
        """Remove a WebSocket connection for a user"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            self._logger.info(f"WebSocket connection removed for user {user_id}")

    async def send_notification(self, user_id: str, notification: Dict[str, Any]):
        """Send a notification to a user through WebSocket"""
        if user_id in self.active_connections:
            try:
                websocket = self.active_connections[user_id]
                
                # Check if the WebSocket is closed
                if websocket.client_state.DISCONNECTED:
                    self._logger.warning(f"WebSocket for user {user_id} is disconnected, removing connection")
                    self.remove_connection(user_id)
                    return False
                    
                # Send the notification
                await websocket.send_json(notification)
                self._logger.info(f"Notification sent to user {user_id} via WebSocket")
                return True
            except RuntimeError as e:
                if "websocket operation outside of a connection" in str(e).lower():
                    self._logger.warning(f"WebSocket for user {user_id} is no longer connected, removing connection")
                    self.remove_connection(user_id)
                else:
                    self._logger.error(f"Runtime error sending notification to user {user_id}: {str(e)}")
                return False
            except Exception as e:
                self._logger.error(f"Error sending notification to user {user_id}: {str(e)}")
                self.remove_connection(user_id)

                return False
        else:
            self._logger.warning(f"No active WebSocket connection for user {user_id}")
        return False

    def start_consumer(self, topic: str, group_id: str, callback: Callable):
        """Start a Kafka consumer for a topic in a background thread"""
        consumer_key = f"{topic}:{group_id}"
        
        # Check if already running
        if consumer_key in self._consumers and self._consumers[consumer_key].is_alive():
            self._logger.info(f"Consumer for {topic} with group {group_id} is already running")
            return
            
        # Create and start consumer thread
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
        retry_interval = 5  # Initial retry interval in seconds
        max_retry_interval = 60
        running = True
        
        while running:
            try:
                consumer = KafkaConsumer(
                    topic,
                    bootstrap_servers=self.bootstrap_servers,
                    group_id=group_id,
                    auto_offset_reset='earliest',
                    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
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
        """Start the notification consumer if not already running"""
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
        """Stop the notification consumer"""
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
                        self._logger.warning(f"Failed to send notification to user {user_id}, no active connection")
                finally:
                    loop.close()
                    
            except Exception as e:
                self._logger.exception(f"Error processing notification message: {str(e)}")
                
        # Start the consumer for the user_notifications topic
        self._logger.info("Starting Kafka consumer for user notifications")
        self.start_consumer("user_notifications", "notification_consumer_group", callback)
                
    def create_job_task(self, job_id: UUID, user_id: UUID, task_type: str, task_data: Optional[Dict] = None):
        """Create a job task in Kafka"""
        message = {
            "job_id": job_id,
            "user_id": user_id,  
            "task_type": task_type,
            "data": task_data or {}
        }
        return self.send_message("job_tasks", message) 
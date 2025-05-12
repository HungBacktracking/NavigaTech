import json
import logging
import threading
import time
from typing import Any, Dict, Optional, Callable
from uuid import UUID

from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError, NoBrokersAvailable
from fastapi import WebSocket

class KafkaService:
    def __init__(self, bootstrap_servers='kafka:9092'):
        self.bootstrap_servers = bootstrap_servers
        self.producer = None
        self.active_connections: Dict[str, WebSocket] = {}
        self._logger = logging.getLogger(__name__)
        self._init_producer()
        
    def _init_producer(self):
        """Initialize Kafka producer with retry logic"""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            self._logger.info("Kafka producer initialized successfully")
        except NoBrokersAvailable:
            self._logger.warning("Kafka brokers not available, will retry later")
            self.producer = None
        except Exception as e:
            self._logger.error(f"Error initializing Kafka producer: {str(e)}")
            self.producer = None

    def _ensure_producer(self):
        """Ensure the producer is initialized"""
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
                await websocket.send_json(notification)
                return True
            except Exception as e:
                self._logger.error(f"Error sending notification to user {user_id}: {str(e)}")
                # Remove the connection if it's closed
                self.remove_connection(user_id)
                return False
        return False

    def start_consumer(self, topic: str, group_id: str, callback: Callable):
        """Start a Kafka consumer for a topic with retry logic"""
        retry_interval = 5  # Initial retry interval in seconds
        max_retry_interval = 60  # Maximum retry interval
        
        while True:
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
                
    def create_job_task(self, job_id: UUID, user_id: UUID, task_type: str, task_data: Optional[Dict] = None):
        """Create a job task in Kafka"""
        message = {
            "job_id": str(job_id),
            "user_id": str(user_id),
            "task_type": task_type,
            "data": task_data or {}
        }
        return self.send_message("job_tasks", message) 
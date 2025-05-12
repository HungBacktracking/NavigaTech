import json
import logging
import threading
import time
from typing import Dict, Any, Optional

from app.model.job_task import TaskStatus, TaskType
from app.services.job_service import JobService
from app.services.job_task_service import JobTaskService
from app.services.kafka_service import KafkaService


class JobWorker:
    def __init__(
        self,
        job_service: JobService,
        job_task_service: JobTaskService,
        kafka_service: KafkaService
    ):
        self.job_service = job_service
        self.job_task_service = job_task_service
        self.kafka_service = kafka_service
        self._logger = logging.getLogger(__name__)
        self._running = False
        self._worker_thread = None

    def start(self):
        """Start the job worker"""
        if self._running:
            return

        self._running = True
        self._worker_thread = threading.Thread(target=self._process_tasks)
        self._worker_thread.daemon = True
        self._worker_thread.start()
        self._logger.info("Job worker started")

    def stop(self):
        """Stop the job worker"""
        if not self._running:
            return
            
        self._logger.info("Stopping job worker...")
        self._running = False
        if self._worker_thread:
            try:
                self._worker_thread.join(timeout=5)
                self._logger.info("Job worker stopped")
            except Exception as e:
                self._logger.error(f"Error stopping job worker: {str(e)}")

    def _process_tasks(self):
        """Process job tasks from Kafka"""
        def callback(message: Dict[str, Any]):
            try:
                job_id = message.get("job_id")
                user_id = message.get("user_id")
                task_type = message.get("task_type")
                
                if not all([job_id, user_id, task_type]):
                    self._logger.error(f"Invalid task message: {message}")
                    return
                
                # Create a task record
                task = self.job_task_service.create_task(
                    job_id=job_id,
                    user_id=user_id,
                    task_type=TaskType(task_type)
                )
                
                self._logger.info(f"Started processing task {task.id} of type {task_type}")
                
                # Update task to processing
                self.job_task_service.update_task_status(task.id, TaskStatus.PROCESSING)
                
                result = None
                error = None
                
                try:
                    # Process the task based on type
                    if task_type == TaskType.JOB_SCORE.value:
                        result = self.job_service.score_job(job_id, user_id)
                    elif task_type == TaskType.JOB_ANALYZE.value:
                        result = self.job_service.analyze_job(job_id, user_id)
                    else:
                        error = f"Unknown task type: {task_type}"
                except Exception as e:
                    error = str(e)
                    self._logger.exception(f"Error processing task {task.id}: {str(e)}")
                
                # Update task status
                if error:
                    self.job_task_service.update_task_status(
                        task.id, TaskStatus.FAILED, error_message=error
                    )
                    self._logger.error(f"Task {task.id} failed: {error}")
                else:
                    self.job_task_service.update_task_status(
                        task.id, TaskStatus.COMPLETED, result=result
                    )
                    self._logger.info(f"Task {task.id} completed successfully")
                
                # Send notification to user
                notification = {
                    "task_id": task.id,
                    "task_type": task_type,
                    "job_id": job_id,
                    "status": TaskStatus.COMPLETED.value if not error else TaskStatus.FAILED.value,
                    "result": result,
                    "error": error
                }
                
                # Use a separate thread to avoid blocking
                notification_thread = threading.Thread(
                    target=self._send_notification,
                    args=(user_id, notification),
                    daemon=True
                )
                notification_thread.start()
                
            except Exception as e:
                self._logger.exception(f"Error processing message: {str(e)}")
        
        try:
            # Start the consumer in a non-blocking way
            self._logger.info("Starting Kafka consumer for job tasks")
            self.kafka_service.start_consumer("job_tasks", "job_worker_group", callback)
        except Exception as e:
            self._logger.error(f"Failed to start Kafka consumer: {str(e)}")
            # If Kafka is down, we'll retry periodically
            while self._running:
                time.sleep(10)
                try:
                    self._logger.info("Retrying to connect to Kafka...")
                    self.kafka_service.start_consumer("job_tasks", "job_worker_group", callback)
                    break
                except Exception as e:
                    self._logger.error(f"Failed to reconnect to Kafka: {str(e)}")
    
    def _send_notification(self, user_id: str, notification: Dict[str, Any]):
        """Send notification to user via Kafka"""
        try:
            self._logger.info(f"Sending notification to user {user_id}")
            result = self.kafka_service.send_message(
                "user_notifications",
                {
                    "user_id": user_id,
                    "notification": notification
                }
            )
            
            if result.get("status") == "error":
                self._logger.error(f"Failed to send notification: {result.get('message')}")
                
        except Exception as e:
            self._logger.exception(f"Error sending notification: {str(e)}") 
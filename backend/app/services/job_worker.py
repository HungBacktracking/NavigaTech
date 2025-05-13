import json
import logging
import threading
import time
import traceback
from typing import Dict, Any, Optional
from uuid import UUID

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
        self._logger.info("JobWorker initialized")

    def start(self):
        """Start the job worker"""
        if self._running:
            self._logger.info("JobWorker already running, ignoring start request")
            return

        self._running = True
        self._worker_thread = threading.Thread(target=self._process_tasks)
        self._worker_thread.daemon = True
        self._worker_thread.start()
        self._logger.info("Job worker started successfully")

    def stop(self):
        """Stop the job worker"""
        if not self._running:
            self._logger.info("JobWorker already stopped, ignoring stop request")
            return
            
        self._logger.info("Stopping job worker...")
        self._running = False
        if self._worker_thread:
            try:
                self._worker_thread.join(timeout=5)
                self._logger.info("Job worker stopped successfully")
            except Exception as e:
                self._logger.error(f"Error stopping job worker: {str(e)}")

    def _process_tasks(self):
        """Process job tasks from Kafka"""
        self._logger.info("Task processor thread started")
        
        def callback(message: Dict[str, Any]):
            task_id = None
            try:
                self._logger.info(f"Received message: {message}")
                
                job_id = message.get("job_id")
                user_id = message.get("user_id")
                task_type = message.get("task_type")
                
                if not all([job_id, user_id, task_type]):
                    self._logger.error(f"Invalid task message, missing required fields: {message}")
                    return
                
                # Create a task record
                task = self.job_task_service.create_task(
                    job_id=UUID(job_id) if isinstance(job_id, str) else job_id,
                    user_id=UUID(user_id) if isinstance(user_id, str) else user_id,
                    task_type=TaskType(task_type)
                )
                
                task_id = task.id
                self._logger.info(f"Created task record {task_id} for job {job_id}, user {user_id}, type {task_type}")
                
                # Update task to processing
                self.job_task_service.update_task_status(task.id, TaskStatus.PROCESSING)
                self._logger.info(f"Task {task_id} status updated to PROCESSING")
                
                result = None
                error = None
                
                try:
                    # Process the task based on type
                    if task_type == TaskType.JOB_SCORE.value:
                        self._logger.info(f"Processing job scoring task for job {job_id}")
                        result = self.job_service.score_job(job_id, user_id)
                        self._logger.info(f"Job scoring completed for job {job_id}")
                    elif task_type == TaskType.JOB_ANALYZE.value:
                        self._logger.info(f"Processing job analysis task for job {job_id}")
                        result = self.job_service.analyze_job(job_id, user_id)
                        self._logger.info(f"Job analysis completed for job {job_id}")
                    else:
                        error = f"Unknown task type: {task_type}"
                        self._logger.error(error)
                except Exception as e:
                    error = str(e)
                    stack_trace = traceback.format_exc()
                    self._logger.exception(f"Error processing task {task.id}: {error}\n{stack_trace}")
                
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
                stack_trace = traceback.format_exc()
                self._logger.exception(f"Unhandled error in task processor: {str(e)}\n{stack_trace}")
                
                # Try to update task status if we have a task_id
                if task_id:
                    try:
                        self.job_task_service.update_task_status(
                            task_id, TaskStatus.FAILED, error_message=f"Unhandled error: {str(e)}"
                        )
                    except Exception as update_error:
                        self._logger.error(f"Failed to update task status: {str(update_error)}")
        
        # Start the consumer in a separate thread through the KafkaService
        self._logger.info("Starting Kafka consumer for job tasks")
        self.kafka_service.start_consumer("job_tasks", "job_worker_group", callback)
        
        # Keep the worker thread alive
        while self._running:
            time.sleep(1)
        
        self._logger.info("Task processor thread exiting")
    
    def _send_notification(self, user_id: str, notification: Dict[str, Any]):
        """Send notification to user via Kafka"""
        try:
            self._logger.info(f"Sending notification to user {user_id} via Kafka")
            result = self.kafka_service.send_message(
                "user_notifications",
                {
                    "user_id": user_id,
                    "notification": notification
                }
            )
            
            if result.get("status") == "error":
                self._logger.error(f"Failed to send notification: {result.get('message')}")
            else:
                self._logger.info(f"Successfully queued notification for user {user_id}")
                
        except Exception as e:
            stack_trace = traceback.format_exc()
            self._logger.exception(f"Error sending notification: {str(e)}\n{stack_trace}") 
import json
import logging
import threading
import time
import traceback
from typing import Dict, Any, Optional
from uuid import UUID

from app.model.job_task import TaskStatus
from app.services.job_service import JobService
from app.services.job_task_service import JobTaskService
from app.services.job_analytic_service import JobAnalyticService
from app.services.kafka_service import KafkaService


class JobWorker:
    def __init__(
            self,
            job_service: JobService,
            job_task_service: JobTaskService,
            kafka_service: KafkaService,
            job_analytic_service: Optional[JobAnalyticService] = None
    ):
        self.job_service = job_service
        self.job_task_service = job_task_service
        self.kafka_service = kafka_service
        self.job_analytic_service = job_analytic_service
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

                if not all([job_id, user_id]):
                    self._logger.error(f"Invalid task message, missing required fields: {message}")
                    return

                # Create a task record
                task = self.job_task_service.create_task(
                    job_id=UUID(job_id) if isinstance(job_id, str) else job_id,
                    user_id=UUID(user_id) if isinstance(user_id, str) else user_id
                )

                task_id = task.id
                self._logger.info(f"Created task record {task_id} for job {job_id}, user {user_id}")

                # Update task to processing
                self.job_task_service.update_task_status(task.id, TaskStatus.PROCESSING)
                self._logger.info(f"Task {task_id} status updated to PROCESSING")

                # Send processing notification
                processing_notification = {
                    "task_id": str(task.id),
                    "job_id": str(job_id),
                    "status": TaskStatus.PROCESSING.value,
                    "message": "Job analysis is processing"
                }
                self._send_notification(user_id, processing_notification)

                result = None
                error = None

                try:
                    if not self.job_analytic_service:
                        error = "JobAnalyticService not initialized"
                        self._logger.error(error)
                    else:
                        self._logger.info(f"Processing complete job analysis task for job {job_id}")

                        # Run scoring and analysis in sequence
                        score_result = self.job_service.score_job(job_id, user_id)
                        self._logger.info(f"Job scoring completed for job {job_id}")

                        # Send progress notification after scoring
                        progress_notification = {
                            "task_id": str(task.id),
                            "job_id": str(job_id),
                            "status": "PROGRESS",
                            "progress": 50,
                            "message": "Job scoring completed, analyzing job details"
                        }
                        self._send_notification(user_id, progress_notification)

                        analysis_result = self.job_service.analyze_job(job_id, user_id)
                        self._logger.info(f"Job analysis completed for job {job_id}")

                        analytic_response = self.job_analytic_service.process_analyze(
                            job_id=UUID(job_id) if isinstance(job_id, str) else job_id,
                            user_id=UUID(user_id) if isinstance(user_id, str) else user_id,
                            score_result=score_result,
                            analysis_result=analysis_result
                        )
                        self._logger.info(f"Combined analysis saved for job {job_id}")

                        # Invalidate relevant caches after job analysis is complete
                        self._invalidate_caches(job_id, user_id)

                        # Convert to dict for result storage
                        result = analytic_response.model_dump()

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
                    "task_id": str(task.id),
                    "job_id": str(job_id),
                    "status": TaskStatus.COMPLETED.value if not error else TaskStatus.FAILED.value,
                    "result": result,
                    "error": error
                }

                # Use a separate thread to avoid blocking
                self._send_notification(user_id, notification)

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

    def _invalidate_caches(self, job_id: Any, user_id: Any):
        """Invalidate all relevant caches after job analysis is complete"""
        try:
            redis_client = self.job_service.redis_client
            if not redis_client:
                self._logger.warning("Redis client not available, skipping cache invalidation")
                return

            # Convert to string if needed
            job_id_str = str(job_id)
            user_id_str = str(user_id)

            # Invalidate specific analysis caches
            redis_client.flush_by_pattern(f"job_analysis:{job_id_str}:{user_id_str}")
            redis_client.flush_by_pattern(f"job_score:{job_id_str}:{user_id_str}")
            
            # Invalidate search results that might contain this job
            redis_client.flush_by_pattern(f"job_search:*:{user_id_str}")
            
            # Invalidate user favorites that contain analysis results
            redis_client.flush_by_pattern(f"user_favorites:{user_id_str}:*")
            
            # Invalidate recommendations if they might include this job
            redis_client.flush_by_pattern(f"job_recommendations:{user_id_str}:*")

            self._logger.info(f"Successfully invalidated caches for job {job_id_str}, user {user_id_str}")
        except Exception as e:
            self._logger.error(f"Error invalidating caches: {str(e)}")

    def _send_notification(self, user_id: str, notification: Dict[str, Any]):
        """Send notification to user via Kafka"""
        try:
            self._logger.info(f"Sending notification to user {user_id} via Kafka")

            # Ensure notification has proper formatting
            if isinstance(notification.get("task_id"), UUID):
                notification["task_id"] = str(notification["task_id"])

            if isinstance(notification.get("job_id"), UUID):
                notification["job_id"] = str(notification["job_id"])

            # Retry logic for sending notifications
            max_retries = 3
            retry_delay = 1  # Initial delay in seconds

            for attempt in range(max_retries):
                result = self.kafka_service.send_message(
                    "user_notifications",
                    {
                        "user_id": user_id,
                        "notification": notification
                    }
                )

                if result.get("status") == "success":
                    self._logger.info(f"Successfully queued notification for user {user_id}")
                    return

                self._logger.warning(
                    f"Failed to send notification (attempt {attempt + 1}/{max_retries}): {result.get('message')}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff

            self._logger.error(f"Failed to send notification after {max_retries} attempts")

        except Exception as e:
            stack_trace = traceback.format_exc()
            self._logger.exception(f"Error sending notification: {str(e)}\n{stack_trace}") 
export interface WebSocketNotification {
  task_id: string;
  job_id: string;
  status: string;
  result: any;
  error?: string;
}

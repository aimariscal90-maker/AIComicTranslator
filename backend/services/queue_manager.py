from datetime import datetime
from typing import Dict, Any, Optional
import uuid

class JobManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(JobManager, cls).__new__(cls)
            cls._instance.jobs = {} # In-memory storage
        return cls._instance

    def create_job(self) -> str:
        job_id = str(uuid.uuid4())
        self.jobs[job_id] = {
            "id": job_id,
            "status": "pending",
            "progress": 0,
            "step": "Initializing",
            "created_at": datetime.now(),
            "result": None,
            "error": None
        }
        return job_id

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        return self.jobs.get(job_id)

    def update_job(self, job_id: str, status: str = None, progress: int = None, step: str = None, result: any = None, error: str = None):
        if job_id in self.jobs:
            if status:
                self.jobs[job_id]["status"] = status
            if progress is not None:
                self.jobs[job_id]["progress"] = progress
            if step:
                self.jobs[job_id]["step"] = step
            if result:
                self.jobs[job_id]["result"] = result
            if error:
                self.jobs[job_id]["error"] = error
                self.jobs[job_id]["status"] = "failed"

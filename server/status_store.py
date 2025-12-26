import json
import time
import uuid
import redis
import os

STATUS_PREFIX = "job:"

class StatusStore:
    def __init__(self, url: str | None = None):
        self.r = redis.Redis.from_url(url or os.environ.get("REDIS_URL"))

    def new_job(self, filename: str) -> str:
        job_id = str(uuid.uuid4())
        data = {
            "id": job_id,
            "filename": filename,
            "status": "RECEIVED",
            "progress": 10,
            "stage": "Upload requested",
            "created_at": int(time.time()),
        }
        self.r.hset(STATUS_PREFIX + job_id, mapping=data)
        # Optional: expire after 24h
        # self.r.expire(STATUS_PREFIX + job_id, 86400)
        return job_id

    def update(self, job_id: str, **fields):
        # Ensure progress never decreases
        if "progress" in fields:
            current = int(self.get(job_id).get("progress", 0) or 0)
            fields["progress"] = max(int(fields["progress"]), current)

        # Auto-set completion timestamp
        if fields.get("status") == "COMPLETED":
            fields["completed_at"] = int(time.time())

        self.r.hset(
            STATUS_PREFIX + job_id,
            mapping={k: str(v) for k, v in fields.items()}
        )

    def get(self, job_id: str) -> dict:
        raw = self.r.hgetall(STATUS_PREFIX + job_id)
        return {k.decode(): v.decode() for k, v in raw.items()} if raw else {}

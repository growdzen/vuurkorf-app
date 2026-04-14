from pydantic import BaseModel, Field
from typing import Optional, Any
from enum import Enum
import uuid


class JobStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class JobStep(str, Enum):
    upload = "upload"
    remove_background = "remove_background"
    silhouette = "silhouette"
    vectorize = "vectorize"
    integrate = "integrate"
    validate = "validate"
    done = "done"


class ProcessingJob(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: JobStatus = JobStatus.pending
    step: Optional[JobStep] = None
    file_path: Optional[str] = None
    material: Optional[str] = None
    thickness: Optional[float] = None
    result: Optional[dict] = None
    error: Optional[str] = None

    class Config:
        use_enum_values = True

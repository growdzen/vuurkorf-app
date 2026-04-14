from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import uuid


class OrderCreate(BaseModel):
    job_id: str
    name: str
    email: str
    material: str
    thickness: float
    scale: float = 1.0
    offset_x: float = 0.0
    offset_y: float = 0.0


class Order(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    job_id: str
    name: str
    email: str
    material: str
    thickness: float
    scale: float = 1.0
    offset_x: float = 0.0
    offset_y: float = 0.0
    price: Optional[float] = None
    status: str = "pending"

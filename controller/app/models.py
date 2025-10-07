from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class NodeRegister(BaseModel):
    node_id: str
    name: str
    address: str
    tags: Optional[List[str]] = []
    api_key: str
    cpu_cores: Optional[int] = 0
    memory_gb: Optional[int] = 0
    disk_gb: Optional[int] = 0


class NodeResponse(BaseModel):
    id: str
    name: str
    address: str
    tags: List[str]
    last_seen: datetime
    status: str
    cpu_cores: int
    memory_gb: int
    disk_gb: int

    class Config:
        from_attributes = True


class StartRequest(BaseModel):
    vehicle_type: str = "copter"
    name: Optional[str] = None
    model: Optional[str] = "iris"
    mav_udp: Optional[int] = None


class StopRequest(BaseModel):
    container_id: Optional[str] = None
    instance_id: Optional[str] = None


class InstanceResponse(BaseModel):
    id: str
    node_id: str
    container_id: Optional[str]
    name: str
    vehicle_type: str
    model: str
    mav_udp: Optional[int]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class LoginRequest(BaseModel):
    username: str
    password: str

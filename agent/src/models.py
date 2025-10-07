from pydantic import BaseModel
from typing import Optional


class StartRequest(BaseModel):
    name: str
    model: str = "iris"
    vehicle_type: str = "copter"
    mav_udp: Optional[int] = None


class StopRequest(BaseModel):
    container_id: Optional[str] = None
    instance_id: Optional[str] = None


class InstanceInfo(BaseModel):
    instance_id: str
    container_id: str
    name: str
    model: str
    vehicle_type: str
    mav_udp: int
    status: str


class NodeStatus(BaseModel):
    node_id: str
    name: str
    status: str
    running_instances: int
    total_cpu_cores: int
    total_memory_gb: int
    total_disk_gb: int
    available_ports: list[int]

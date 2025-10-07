from pydantic_settings import BaseSettings
from typing import Optional
import socket
import os


class Settings(BaseSettings):
    # Agent configuration
    node_id: str = f"node-{socket.gethostname()}"
    name: str = socket.gethostname()
    public_address: Optional[str] = None
    port: int = 8443
    host: str = "0.0.0.0"
    
    # Controller configuration
    controller_url: str = "https://localhost:8000/api/v1/register"
    agent_api_key: str = "agent-registration-key"
    
    # Docker configuration
    docker_socket: str = "unix:///var/run/docker.sock"
    px4_image: str = "px4io/px4-dev-simulation:latest"
    
    # Port allocation
    mav_port_start: int = 14560
    mav_port_end: int = 14570
    
    # System resources
    cpu_cores: int = 4
    memory_gb: int = 8
    disk_gb: int = 50
    
    class Config:
        env_file = ".env"


settings = Settings()

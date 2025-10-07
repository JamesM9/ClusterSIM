import docker
import uuid
import subprocess
import psutil
from typing import Dict, List, Optional
from src.config import settings
from src.models import InstanceInfo


class DockerManager:
    def __init__(self):
        self.client = docker.from_env()
        self.used_ports = set()
        self.running_instances: Dict[str, InstanceInfo] = {}
    
    def get_available_port(self) -> int:
        """Get an available MAVLink UDP port"""
        for port in range(settings.mav_port_start, settings.mav_port_end + 1):
            if port not in self.used_ports:
                self.used_ports.add(port)
                return port
        raise Exception("No available ports")
    
    def release_port(self, port: int):
        """Release a port back to the pool"""
        self.used_ports.discard(port)
    
    def start_px4_instance(self, request) -> InstanceInfo:
        """Start a new PX4 SITL instance in Docker"""
        # Get available port
        mav_port = request.mav_udp or self.get_available_port()
        
        # Generate unique identifiers
        instance_id = str(uuid.uuid4())
        container_name = f"px4_{request.name}_{instance_id[:8]}"
        
        # Build PX4 command
        px4_cmd = [
            "bash", "-lc",
            f"""
            HEADLESS=1 PX4_INSTANCE=0 make px4_sitl gazebo_{request.model} PX4_SIM_UDP_PORT={mav_port}
            """
        ]
        
        try:
            # Create and run container
            container = self.client.containers.run(
                settings.px4_image,
                command=px4_cmd,
                name=container_name,
                detach=True,
                remove=True,
                ports={f"{mav_port}/udp": mav_port},
                environment={
                    "PX4_SIM_UDP_PORT": str(mav_port),
                    "HEADLESS": "1",
                    "PX4_INSTANCE": "0"
                },
                volumes={
                    "/tmp/.X11-unix": {"bind": "/tmp/.X11-unix", "mode": "ro"}
                },
                network_mode="host"  # Use host networking for simplicity
            )
            
            # Create instance info
            instance_info = InstanceInfo(
                instance_id=instance_id,
                container_id=container.id,
                name=request.name,
                model=request.model,
                vehicle_type=request.vehicle_type,
                mav_udp=mav_port,
                status="running"
            )
            
            # Store instance info
            self.running_instances[instance_id] = instance_info
            
            return instance_info
            
        except Exception as e:
            # Release port if container creation failed
            self.release_port(mav_port)
            raise Exception(f"Failed to start PX4 container: {str(e)}")
    
    def stop_instance(self, request) -> Dict[str, str]:
        """Stop a PX4 instance"""
        container_id = None
        instance_id = None
        
        if request.container_id:
            container_id = request.container_id
        elif request.instance_id:
            instance_info = self.running_instances.get(request.instance_id)
            if instance_info:
                container_id = instance_info.container_id
                instance_id = request.instance_id
        
        if not container_id:
            raise Exception("Container ID or Instance ID required")
        
        try:
            # Stop and remove container
            container = self.client.containers.get(container_id)
            container.stop(timeout=10)
            
            # Release port
            if instance_id and instance_id in self.running_instances:
                instance_info = self.running_instances[instance_id]
                self.release_port(instance_info.mav_udp)
                del self.running_instances[instance_id]
            
            return {
                "status": "stopped",
                "container_id": container_id,
                "instance_id": instance_id
            }
            
        except Exception as e:
            raise Exception(f"Failed to stop container: {str(e)}")
    
    def list_instances(self) -> List[InstanceInfo]:
        """List all running instances"""
        # Update instance statuses
        for instance_info in self.running_instances.values():
            try:
                container = self.client.containers.get(instance_info.container_id)
                instance_info.status = "running" if container.status == "running" else "stopped"
            except:
                instance_info.status = "stopped"
        
        return list(self.running_instances.values())
    
    def get_system_resources(self) -> Dict[str, int]:
        """Get system resource information"""
        return {
            "cpu_cores": psutil.cpu_count(),
            "memory_gb": int(psutil.virtual_memory().total / (1024**3)),
            "disk_gb": int(psutil.disk_usage('/').total / (1024**3))
        }
    
    def get_available_ports(self) -> List[int]:
        """Get list of available ports"""
        available = []
        for port in range(settings.mav_port_start, settings.mav_port_end + 1):
            if port not in self.used_ports:
                available.append(port)
        return available

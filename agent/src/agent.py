#!/usr/bin/env python3
"""
PX4 Agent - Runs on Azure VMs to manage PX4 SITL instances
"""
import asyncio
import socket
import sys
import argparse
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import uvicorn

from src.config import settings
from src.models import StartRequest, StopRequest, InstanceInfo, NodeStatus
from src.docker_manager import DockerManager


# Global Docker manager instance
docker_manager = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global docker_manager
    
    # Startup
    docker_manager = DockerManager()
    
    # Register with controller
    await register_with_controller()
    
    yield
    
    # Shutdown - cleanup any running containers
    if docker_manager:
        for instance_info in docker_manager.list_instances():
            try:
                docker_manager.stop_instance(StopRequest(instance_id=instance_info.instance_id))
            except:
                pass


app = FastAPI(
    title="PX4 Agent",
    description="Agent service for managing PX4 SITL instances on Azure VMs",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def register_with_controller():
    """Register this agent with the controller"""
    try:
        # Get public IP if not set
        public_address = settings.public_address
        if not public_address:
            # Try to get public IP
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                    s.connect(("8.8.8.8", 80))
                    public_address = s.getsockname()[0]
            except:
                public_address = "127.0.0.1"
        
        # Get system resources
        resources = docker_manager.get_system_resources() if docker_manager else {
            "cpu_cores": settings.cpu_cores,
            "memory_gb": settings.memory_gb,
            "disk_gb": settings.disk_gb
        }
        
        registration_data = {
            "node_id": settings.node_id,
            "name": settings.name,
            "address": public_address,
            "tags": ["px4-agent", "azure-vm"],
            "api_key": settings.agent_api_key,
            "cpu_cores": resources["cpu_cores"],
            "memory_gb": resources["memory_gb"],
            "disk_gb": resources["disk_gb"]
        }
        
        async with httpx.AsyncClient(verify=False, timeout=10) as client:
            response = await client.post(settings.controller_url, json=registration_data)
            if response.status_code == 200:
                print(f"Successfully registered with controller: {response.json()}")
            else:
                print(f"Failed to register with controller: {response.status_code} - {response.text}")
                
    except Exception as e:
        print(f"Registration failed: {e}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "node_id": settings.node_id,
        "timestamp": "2024-01-01T00:00:00Z"  # In production, use actual timestamp
    }


@app.get("/agent/status", response_model=NodeStatus)
async def get_agent_status():
    """Get agent status and running instances"""
    if not docker_manager:
        raise HTTPException(status_code=500, detail="Docker manager not initialized")
    
    instances = docker_manager.list_instances()
    running_count = len([i for i in instances if i.status == "running"])
    
    resources = docker_manager.get_system_resources()
    available_ports = docker_manager.get_available_ports()
    
    return NodeStatus(
        node_id=settings.node_id,
        name=settings.name,
        status="online",
        running_instances=running_count,
        total_cpu_cores=resources["cpu_cores"],
        total_memory_gb=resources["memory_gb"],
        total_disk_gb=resources["disk_gb"],
        available_ports=available_ports
    )


@app.get("/agent/instances", response_model=List[InstanceInfo])
async def list_instances():
    """List all running instances on this agent"""
    if not docker_manager:
        raise HTTPException(status_code=500, detail="Docker manager not initialized")
    
    return docker_manager.list_instances()


@app.post("/agent/start", response_model=InstanceInfo)
async def start_instance(request: StartRequest):
    """Start a new PX4 instance"""
    if not docker_manager:
        raise HTTPException(status_code=500, detail="Docker manager not initialized")
    
    try:
        instance_info = docker_manager.start_px4_instance(request)
        
        # Update controller with instance info
        await update_controller_instance(instance_info)
        
        return instance_info
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agent/stop")
async def stop_instance(request: StopRequest):
    """Stop a PX4 instance"""
    if not docker_manager:
        raise HTTPException(status_code=500, detail="Docker manager not initialized")
    
    try:
        result = docker_manager.stop_instance(request)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def update_controller_instance(instance_info: InstanceInfo):
    """Update controller with instance information"""
    # This could be used to send instance updates back to controller
    # For now, we'll just log it
    print(f"Instance {instance_info.name} started with ID {instance_info.instance_id}")


def main():
    parser = argparse.ArgumentParser(description="PX4 Agent")
    parser.add_argument("--host", default=settings.host, help="Host to bind to")
    parser.add_argument("--port", default=settings.port, help="Port to bind to")
    parser.add_argument("--node-id", default=settings.node_id, help="Node ID")
    parser.add_argument("--controller-url", default=settings.controller_url, help="Controller registration URL")
    
    args = parser.parse_args()
    
    # Update settings with command line arguments
    settings.host = args.host
    settings.port = args.port
    settings.node_id = args.node_id
    settings.controller_url = args.controller_url
    
    print(f"Starting PX4 Agent on {settings.host}:{settings.port}")
    print(f"Node ID: {settings.node_id}")
    print(f"Controller URL: {settings.controller_url}")
    
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level="info"
    )


if __name__ == "__main__":
    main()

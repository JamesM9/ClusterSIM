from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
import json
from datetime import datetime, timedelta

from app.database import get_db, Node, Instance, User, engine
from app.models import (
    NodeRegister, NodeResponse, StartRequest, StopRequest, InstanceResponse,
    UserCreate, UserResponse, Token, LoginRequest
)
from app.auth import (
    create_access_token, authenticate_user, get_current_active_user,
    get_password_hash, verify_password
)
from app.agent_client import agent_client
from app.config import settings

# Create FastAPI app
app = FastAPI(
    title="PX4 Cloud Controller",
    description="Central controller for managing PX4 SITL instances on Azure VMs",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()


# --- Authentication Endpoints ---

@app.post("/auth/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )
    
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        id=str(uuid.uuid4()),
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/auth/login", response_model=Token)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Login and get access token"""
    user = authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# --- Node Management ---

@app.post("/api/v1/register")
async def register_node(reg: NodeRegister, db: Session = Depends(get_db)):
    """Register a worker node with the controller"""
    if reg.api_key != settings.agent_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid agent API key"
        )
    
    # Check if node already exists
    existing_node = db.query(Node).filter(Node.id == reg.node_id).first()
    
    if existing_node:
        # Update existing node
        existing_node.name = reg.name
        existing_node.address = reg.address
        existing_node.tags = json.dumps(reg.tags)
        existing_node.last_seen = datetime.utcnow()
        existing_node.status = "online"
        existing_node.cpu_cores = reg.cpu_cores
        existing_node.memory_gb = reg.memory_gb
        existing_node.disk_gb = reg.disk_gb
    else:
        # Create new node
        new_node = Node(
            id=reg.node_id,
            name=reg.name,
            address=reg.address,
            tags=json.dumps(reg.tags),
            status="online",
            cpu_cores=reg.cpu_cores,
            memory_gb=reg.memory_gb,
            disk_gb=reg.disk_gb
        )
        db.add(new_node)
    
    db.commit()
    return {"status": "registered", "node_id": reg.node_id}


@app.get("/api/v1/nodes", response_model=List[NodeResponse])
async def list_nodes(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List all registered nodes"""
    nodes = db.query(Node).all()
    return [
        NodeResponse(
            id=node.id,
            name=node.name,
            address=node.address,
            tags=json.loads(node.tags) if node.tags else [],
            last_seen=node.last_seen,
            status=node.status,
            cpu_cores=node.cpu_cores,
            memory_gb=node.memory_gb,
            disk_gb=node.disk_gb
        )
        for node in nodes
    ]


@app.get("/api/v1/nodes/{node_id}", response_model=NodeResponse)
async def get_node(
    node_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get details of a specific node"""
    node = db.query(Node).filter(Node.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    
    return NodeResponse(
        id=node.id,
        name=node.name,
        address=node.address,
        tags=json.loads(node.tags) if node.tags else [],
        last_seen=node.last_seen,
        status=node.status,
        cpu_cores=node.cpu_cores,
        memory_gb=node.memory_gb,
        disk_gb=node.disk_gb
    )


# --- Instance Management ---

@app.post("/api/v1/nodes/{node_id}/start")
async def start_instance(
    node_id: str,
    body: StartRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Start a PX4 instance on a specific node"""
    # Find node
    node = db.query(Node).filter(Node.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    
    # Check if node is online
    if node.status != "online":
        raise HTTPException(status_code=400, detail="Node is not online")
    
    # Generate instance name if not provided
    instance_name = body.name or f"sim-{uuid.uuid4().hex[:6]}"
    
    # Prepare request for agent
    agent_request = {
        "name": instance_name,
        "model": body.model,
        "vehicle_type": body.vehicle_type,
        "mav_udp": body.mav_udp
    }
    
    try:
        # Call agent to start instance
        agent_url = f"https://{node.address}:8443"
        response = await agent_client.start_instance(agent_url, agent_request)
        
        # Create instance record
        instance_id = response.get("instance_id", str(uuid.uuid4()))
        new_instance = Instance(
            id=instance_id,
            node_id=node_id,
            container_id=response.get("container_id"),
            name=instance_name,
            vehicle_type=body.vehicle_type,
            model=body.model,
            mav_udp=response.get("mav_udp"),
            status="running"
        )
        db.add(new_instance)
        db.commit()
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start instance: {str(e)}")


@app.post("/api/v1/nodes/{node_id}/stop")
async def stop_instance(
    node_id: str,
    body: StopRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Stop a PX4 instance on a specific node"""
    # Find node
    node = db.query(Node).filter(Node.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    
    # Find instance
    instance = None
    if body.instance_id:
        instance = db.query(Instance).filter(Instance.id == body.instance_id).first()
    elif body.container_id:
        instance = db.query(Instance).filter(Instance.container_id == body.container_id).first()
    
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    
    try:
        # Call agent to stop instance
        agent_url = f"https://{node.address}:8443"
        response = await agent_client.stop_instance(agent_url, {
            "container_id": instance.container_id,
            "instance_id": instance.id
        })
        
        # Update instance status
        instance.status = "stopped"
        instance.updated_at = datetime.utcnow()
        db.commit()
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop instance: {str(e)}")


@app.get("/api/v1/instances", response_model=List[InstanceResponse])
async def list_instances(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List all instances"""
    instances = db.query(Instance).all()
    return instances


@app.get("/api/v1/instances/{instance_id}", response_model=InstanceResponse)
async def get_instance(
    instance_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get details of a specific instance"""
    instance = db.query(Instance).filter(Instance.id == instance_id).first()
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    
    return instance


# --- Health Check ---

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)

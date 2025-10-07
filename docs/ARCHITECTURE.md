# PX4 Cloud Simulator - Architecture Overview

This document provides a detailed overview of the PX4 Cloud Simulator architecture, components, and their interactions.

## High-Level Architecture

```
┌─────────────────┐    HTTPS     ┌─────────────────┐    HTTPS     ┌─────────────────┐
│   User Browser  │◄────────────►│   Controller    │◄────────────►│  Agent VMs      │
│                 │              │   (FastAPI)     │              │  (Azure VMs)    │
└─────────────────┘              └─────────────────┘              └─────────────────┘
                                         │                                │
                                         │                                │
                                         ▼                                ▼
                                 ┌─────────────────┐              ┌─────────────────┐
                                 │   Database      │              │  Docker Engine  │
                                 │  (PostgreSQL)   │              │  (PX4 Containers)│
                                 └─────────────────┘              └─────────────────┘
```

## Component Overview

### 1. Controller (FastAPI Server)

**Purpose**: Central orchestrator that manages the entire PX4 simulation fleet.

**Responsibilities**:
- User authentication and authorization
- Node (agent) registration and management
- Instance lifecycle management (start/stop)
- Database operations
- API endpoint exposure
- Frontend serving (static files)

**Technology Stack**:
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL (production) / SQLite (development)
- **Authentication**: JWT tokens
- **ORM**: SQLAlchemy
- **HTTP Client**: httpx (async)

**Key Modules**:
- `app/main.py` - Main FastAPI application
- `app/database.py` - Database models and connection
- `app/auth.py` - Authentication and authorization
- `app/models.py` - Pydantic models for API
- `app/agent_client.py` - HTTP client for agent communication

### 2. Agent Service (Worker VMs)

**Purpose**: Runs on each Azure VM to manage local PX4 SITL instances.

**Responsibilities**:
- Register with controller on startup
- Start/stop PX4 Docker containers
- Monitor container health and resource usage
- Expose local API for controller communication
- Port management for MAVLink connections

**Technology Stack**:
- **Framework**: FastAPI (Python)
- **Container Runtime**: Docker
- **PX4 Image**: `px4io/px4-dev-simulation:latest`
- **System Monitoring**: psutil

**Key Modules**:
- `src/agent.py` - Main agent application
- `src/docker_manager.py` - Docker container management
- `src/config.py` - Agent configuration
- `src/models.py` - Pydantic models

### 3. Frontend (React Web GUI)

**Purpose**: User interface for managing the simulation fleet.

**Responsibilities**:
- User authentication interface
- Node and instance visualization
- Instance management (start/stop)
- Real-time status updates
- MAVLink connection information

**Technology Stack**:
- **Framework**: React 18
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios
- **Icons**: Lucide React
- **Build Tool**: Create React App

**Key Components**:
- `src/App.js` - Main application component
- `src/components/Login.js` - Authentication interface
- `src/components/NodeCard.js` - Node management interface
- `src/components/InstanceList.js` - Instance listing and management
- `src/services/api.js` - API client with authentication

### 4. Database (PostgreSQL/SQLite)

**Purpose**: Persistent storage for system state.

**Tables**:
- `nodes` - Worker VM information
- `instances` - PX4 simulation instances
- `users` - User accounts and authentication

**Key Fields**:
- Node: ID, name, address, resources, status, last_seen
- Instance: ID, node_id, container_id, name, ports, status
- User: ID, username, email, hashed_password, is_active

## Data Flow

### 1. User Authentication Flow

```
User Browser → Controller /auth/login → JWT Token → Store in localStorage
```

### 2. Node Registration Flow

```
Agent Startup → POST /api/v1/register → Controller DB → Node Available
```

### 3. Instance Start Flow

```
User Request → Controller API → Agent API → Docker Container → MAVLink Port
```

### 4. Instance Monitoring Flow

```
Docker Container → Agent Health Check → Controller DB → Frontend Display
```

## Network Architecture

### Port Allocation

| Service | Port | Protocol | Purpose |
|---------|------|----------|---------|
| Controller API | 8000 | HTTP/HTTPS | REST API |
| Frontend | 80/443 | HTTP/HTTPS | Web interface |
| Agent API | 8443 | HTTPS | Agent communication |
| MAVLink | 14560-14570 | UDP | PX4 telemetry |
| PostgreSQL | 5432 | TCP | Database |

### Security Zones

1. **Public Zone**: Controller frontend (port 80/443)
2. **API Zone**: Controller API (port 8000)
3. **Agent Zone**: Agent APIs (port 8443, restricted to controller)
4. **MAVLink Zone**: PX4 telemetry (UDP ports, can be public)

## Deployment Architectures

### 1. Development (Local)

```
┌─────────────────────────────────────────────────┐
│                Local Machine                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │
│  │ Controller  │  │   Agent     │  │Frontend │ │
│  │ (FastAPI)   │  │ (FastAPI)   │  │ (React) │ │
│  │ Port 8000   │  │ Port 8443   │  │Port 3000│ │
│  └─────────────┘  └─────────────┘  └─────────┘ │
│         │                │              │       │
│         └────────────────┼──────────────┘       │
│                          │                      │
│                   ┌─────────────┐               │
│                   │   Docker    │               │
│                   │ (PX4 SITL)  │               │
│                   └─────────────┘               │
└─────────────────────────────────────────────────┘
```

### 2. Docker Compose

```
┌─────────────────────────────────────────────────┐
│              Docker Compose                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │
│  │ PostgreSQL  │  │ Controller  │  │Frontend │ │
│  │   :5432     │  │   :8000     │  │  :80    │ │
│  └─────────────┘  └─────────────┘  └─────────┘ │
│         │                │              │       │
│         └────────────────┼──────────────┘       │
│                          │                      │
│                   ┌─────────────┐               │
│                   │   Agent     │               │
│                   │   :8443     │               │
│                   └─────────────┘               │
└─────────────────────────────────────────────────┘
```

### 3. Azure Production

```
┌─────────────────────────────────────────────────────────────────┐
│                        Azure Cloud                             │
│                                                                 │
│  ┌─────────────────┐              ┌─────────────────────────┐  │
│  │  Controller VM  │              │     Agent VMs           │  │
│  │  ┌───────────┐  │              │  ┌─────┐  ┌─────┐       │  │
│  │  │Controller │  │              │  │Agent1│  │Agent2│     │  │
│  │  │:8000      │  │              │  └─────┘  └─────┘       │  │
│  │  └───────────┘  │              │     │        │          │  │
│  │  ┌───────────┐  │              │     ▼        ▼          │  │
│  │  │Frontend   │  │              │  ┌─────────────────────┐ │  │
│  │  │:80        │  │              │  │  Docker Containers  │ │  │
│  │  └───────────┘  │              │  │  (PX4 SITL)        │ │  │
│  └─────────────────┘              │  └─────────────────────┘ │  │
│           │                       └─────────────────────────┘  │
│           ▼                                                   │
│  ┌─────────────────┐                                         │
│  │   PostgreSQL    │                                         │
│  │   Database      │                                         │
│  └─────────────────┘                                         │
└─────────────────────────────────────────────────────────────────┘
```

## Security Architecture

### Authentication & Authorization

1. **User Authentication**: JWT tokens with configurable expiration
2. **Agent Authentication**: API key-based registration
3. **Role-based Access**: User roles (admin, user) - future enhancement
4. **Session Management**: Stateless JWT approach

### Network Security

1. **HTTPS/TLS**: All communications encrypted in production
2. **Network Segmentation**: Agents isolated behind firewalls
3. **Port Restrictions**: Only necessary ports exposed
4. **API Rate Limiting**: Protection against abuse

### Container Security

1. **Docker Isolation**: PX4 instances run in isolated containers
2. **Resource Limits**: CPU and memory constraints
3. **Network Isolation**: Container networking with port mapping
4. **Image Security**: Official PX4 images from trusted registry

## Scalability Considerations

### Horizontal Scaling

1. **Agent VMs**: Add more worker VMs as needed
2. **Load Balancing**: Multiple controller instances behind load balancer
3. **Database Scaling**: Read replicas for high availability
4. **Container Orchestration**: Kubernetes deployment option

### Vertical Scaling

1. **VM Sizes**: Increase VM sizes for more resources
2. **Database Tuning**: Optimize PostgreSQL configuration
3. **Caching**: Redis for session and data caching
4. **Connection Pooling**: Database connection optimization

### Performance Optimization

1. **Async Operations**: FastAPI async/await for I/O operations
2. **Database Indexing**: Optimized queries with proper indexes
3. **Frontend Optimization**: React lazy loading and code splitting
4. **CDN Integration**: Static asset delivery optimization

## Monitoring & Observability

### Metrics Collection

1. **System Metrics**: CPU, memory, disk usage per node
2. **Application Metrics**: API response times, error rates
3. **Container Metrics**: Docker container health and resource usage
4. **Business Metrics**: Instance count, user activity

### Logging Strategy

1. **Centralized Logging**: All services log to centralized system
2. **Structured Logging**: JSON format for easy parsing
3. **Log Levels**: Appropriate log levels for different environments
4. **Log Rotation**: Prevent disk space issues

### Health Checks

1. **Controller Health**: `/health` endpoint for load balancer
2. **Agent Health**: Periodic health checks and registration
3. **Database Health**: Connection pool monitoring
4. **Container Health**: Docker health checks

## Disaster Recovery

### Backup Strategy

1. **Database Backups**: Automated PostgreSQL backups
2. **Configuration Backups**: Infrastructure as Code (Terraform)
3. **Application Backups**: Container images and configurations
4. **User Data Backups**: Instance configurations and logs

### High Availability

1. **Multi-AZ Deployment**: Azure Availability Zones
2. **Database Clustering**: PostgreSQL high availability setup
3. **Load Balancer**: Traffic distribution and failover
4. **Auto-scaling**: Automatic VM scaling based on demand

## Future Enhancements

### Planned Features

1. **Multi-tenancy**: Organization and project-based isolation
2. **Advanced Scheduling**: Instance scheduling and automation
3. **MAVLink Routing**: Centralized telemetry routing
4. **Plugin System**: Extensible architecture for custom features
5. **Mobile App**: Native mobile application for monitoring

### Technology Upgrades

1. **Kubernetes**: Container orchestration for better scalability
2. **GraphQL**: More efficient API queries
3. **WebSockets**: Real-time updates without polling
4. **Microservices**: Further service decomposition
5. **Event Streaming**: Apache Kafka for event-driven architecture

This architecture provides a solid foundation for managing PX4 simulations at scale while maintaining security, reliability, and ease of use.

# PX4 Cloud Simulator — Server Control + WebGUI

A complete FastAPI server controller with web GUI for managing PX4 SITL instances running on Azure VMs.

## Architecture

```
[User's Browser] <--HTTPS--> [Controller (FastAPI + React)] <--HTTPS--> [Azure VM Agents (HTTPS)]
                               |                             |
                             DB (Postgres/SQLite)        Docker (PX4 SITL containers)
                               |
                            MAVLink Router (optional)
```

## Features

- Central controller with REST API and web GUI
- Worker agents on Azure VMs for PX4 SITL instance management
- Docker-based PX4 SITL containers for isolation
- JWT authentication and secure agent communication
- Real-time instance monitoring and control
- MAVLink endpoint management for QGroundControl integration

## Quick Start

### Controller Setup
```bash
cd controller
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Agent Setup (on Azure VM)
```bash
cd agent
pip install -r requirements.txt
python src/agent.py --host 0.0.0.0 --port 8443
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

## Project Structure

- `controller/` - FastAPI server with REST API and database
- `agent/` - VM agent service for managing PX4 containers
- `frontend/` - React web GUI
- `deployment/` - Docker, cloud-init, and Terraform configurations
- `docs/` - Documentation and setup guides

## Security

- JWT token authentication for users
- API key authentication for agent registration
- TLS encryption for all communications
- Azure NSG rules for network security
- Docker container isolation

## License

MIT License
# ClusterSIM

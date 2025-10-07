# PX4 Cloud Simulator - Quick Start Guide

Get up and running with the PX4 Cloud Simulator in minutes!

## Option 1: Docker Compose (Recommended)

The fastest way to get started:

```bash
# Clone the repository
git clone <repository-url>
cd ClusterSIM

# Start all services
cd deployment/docker
docker-compose up -d

# Wait for services to start (about 2-3 minutes)
docker-compose logs -f
```

Access the web interface at: http://localhost

**Default credentials:**
- Username: `admin`
- Password: `admin123` (change this in production!)

## Option 2: Local Development

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker

### 1. Start the Controller

```bash
cd controller
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

The controller will start on http://localhost:8000

### 2. Start an Agent (Local)

```bash
cd agent
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp env.example .env
# Edit .env to point to controller: CONTROLLER_URL=http://localhost:8000/api/v1/register
python run.py
```

### 3. Start the Frontend

```bash
cd frontend
npm install
npm start
```

The web interface will start on http://localhost:3000

## First Steps

### 1. Create a User Account

If this is your first time, register a new user:

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@example.com", 
    "password": "admin123"
  }'
```

### 2. Login to Web Interface

1. Open http://localhost (or http://localhost:3000 for local dev)
2. Login with your credentials
3. You should see the dashboard

### 3. Start Your First PX4 Instance

1. In the web interface, find an available node
2. Click "Start Instance" on a node
3. Fill in the details:
   - **Name**: `my-first-sim` (optional)
   - **Model**: `iris` (recommended for beginners)
   - **Vehicle Type**: `copter`
4. Click "Start"

### 4. Connect with QGroundControl

1. Download and install [QGroundControl](https://qgroundcontrol.com/)
2. In QGroundControl, go to Application Settings → Comm Links
3. Add a new UDP connection:
   - **Host**: `localhost` (or your agent's IP)
   - **Port**: `14560` (or the port shown in the web interface)
4. Connect to start controlling your simulated drone!

## What You'll See

### Dashboard
- **Total Nodes**: Number of worker VMs registered
- **Online Nodes**: Nodes currently available
- **Total Instances**: All PX4 instances (running and stopped)
- **Running Instances**: Currently active simulations

### Nodes Section
- List of all worker VMs
- System resources (CPU, RAM, Disk)
- Running instances on each node
- Start new instances

### Instances Section
- All PX4 instances across all nodes
- Instance status (running, stopped, error)
- MAVLink connection details
- Quick actions (stop, connect to QGroundControl)

## Troubleshooting

### Agent Not Showing Up

If you don't see any nodes in the web interface:

1. **Check agent logs**:
   ```bash
   # For Docker
   docker-compose logs agent
   
   # For local agent
   tail -f agent.log
   ```

2. **Verify network connectivity**:
   ```bash
   curl http://localhost:8000/health
   ```

3. **Check agent configuration**:
   - Ensure `CONTROLLER_URL` points to your controller
   - Verify `AGENT_API_KEY` matches the controller's key

### PX4 Instance Won't Start

1. **Check Docker is running**:
   ```bash
   docker ps
   ```

2. **Verify PX4 image is available**:
   ```bash
   docker images | grep px4
   ```

3. **Check port availability**:
   ```bash
   netstat -tulpn | grep 14560
   ```

### Can't Connect with QGroundControl

1. **Verify the port number** in the web interface
2. **Check firewall settings** - ensure UDP ports 14560-14570 are open
3. **Try different connection types**:
   - UDP connection to localhost:14560
   - TCP connection (if supported by your setup)

### Web Interface Issues

1. **Clear browser cache** and refresh
2. **Check browser console** for JavaScript errors
3. **Verify API connectivity**:
   ```bash
   curl http://localhost:8000/api/v1/nodes
   ```

## Next Steps

### Production Deployment

Once you're comfortable with the system:

1. **Read the full [Deployment Guide](DEPLOYMENT.md)**
2. **Set up Azure VMs** using the Terraform configurations
3. **Configure SSL certificates** for HTTPS
4. **Set up monitoring and logging**
5. **Implement backup strategies**

### Customization

- **Modify PX4 models**: Edit the available models in the frontend
- **Add custom vehicle types**: Extend the API and frontend
- **Integrate with other tools**: Use the REST API to build custom integrations
- **Scale horizontally**: Add more agent VMs as needed

### Advanced Features

- **MAVLink routing**: Set up centralized MAVLink routing for multiple clients
- **Instance scheduling**: Automate instance lifecycle management
- **Resource monitoring**: Track CPU, memory, and network usage
- **Multi-user support**: Implement user roles and permissions

## Getting Help

1. **Check the logs** first - most issues are visible in the logs
2. **Review the [API Documentation](API.md)** for integration details
3. **Look at the [Deployment Guide](DEPLOYMENT.md)** for production setup
4. **Create an issue** in the repository if you need additional help

## Common Commands

```bash
# Check service status (Docker)
docker-compose ps

# View logs
docker-compose logs -f [service-name]

# Restart a service
docker-compose restart [service-name]

# Stop all services
docker-compose down

# Update and restart
docker-compose pull
docker-compose up -d --build
```

Happy simulating! 🚁

# PX4 Cloud Simulator - Deployment Guide

This guide covers different deployment options for the PX4 Cloud Simulator system.

## Table of Contents

1. [Local Development Setup](#local-development-setup)
2. [Docker Deployment](#docker-deployment)
3. [Azure VM Deployment](#azure-vm-deployment)
4. [Production Deployment](#production-deployment)
5. [Configuration](#configuration)
6. [Troubleshooting](#troubleshooting)

## Local Development Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker
- Git

### 1. Clone the Repository

```bash
git clone <repository-url>
cd ClusterSIM
```

### 2. Setup Controller

```bash
cd controller
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp env.example .env
# Edit .env with your configuration
python run.py
```

### 3. Setup Agent (Local Testing)

```bash
cd agent
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp env.example .env
# Edit .env to point to your controller
python run.py
```

### 4. Setup Frontend

```bash
cd frontend
npm install
cp env.example .env
# Edit .env with your API URL
npm start
```

## Docker Deployment

### Quick Start with Docker Compose

```bash
cd deployment/docker
docker-compose up -d
```

This will start:
- PostgreSQL database
- Controller API
- Frontend web interface
- Example agent

### Access the Application

- Web Interface: http://localhost
- API: http://localhost:8000
- Database: localhost:5432

### Custom Configuration

1. Copy and edit environment files:
```bash
cp controller/env.example controller/.env
cp agent/env.example agent/.env
cp frontend/env.example frontend/.env
```

2. Modify `docker-compose.yml` as needed

3. Rebuild and restart:
```bash
docker-compose down
docker-compose up -d --build
```

## Azure VM Deployment

### Prerequisites

- Azure CLI installed and configured
- Terraform installed
- SSH key pair generated

### 1. Terraform Deployment

```bash
cd deployment/terraform

# Copy and edit variables
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values

# Initialize Terraform
terraform init

# Plan deployment
terraform plan

# Deploy infrastructure
terraform apply
```

### 2. Manual Azure VM Setup

If you prefer to set up VMs manually:

#### Controller VM Setup

```bash
# Create VM with Ubuntu 20.04 LTS
az vm create \
  --resource-group px4-cloud-sim \
  --name px4-controller \
  --image UbuntuLTS \
  --size Standard_B2s \
  --admin-username azureuser \
  --ssh-key-value ~/.ssh/id_rsa.pub \
  --public-ip-sku Standard

# Install dependencies
ssh azureuser@<controller-ip>
sudo apt update && sudo apt upgrade -y
sudo apt install -y docker.io python3-pip git
sudo systemctl enable docker
sudo usermod -aG docker azureuser

# Clone and setup controller
git clone <repository-url>
cd ClusterSIM/controller
pip3 install -r requirements.txt
python3 run.py
```

#### Agent VM Setup

```bash
# Create agent VM
az vm create \
  --resource-group px4-cloud-sim \
  --name px4-agent-01 \
  --image UbuntuLTS \
  --size Standard_B4ms \
  --admin-username azureuser \
  --ssh-key-value ~/.ssh/id_rsa.pub

# Setup agent
ssh azureuser@<agent-ip>
sudo apt update && sudo apt upgrade -y
sudo apt install -y docker.io python3-pip git
sudo systemctl enable docker
sudo usermod -aG docker azureuser

# Install PX4 image
docker pull px4io/px4-dev-simulation:latest

# Setup agent service
git clone <repository-url>
cd ClusterSIM/agent
pip3 install -r requirements.txt
cp env.example .env
# Edit .env with controller URL
python3 run.py
```

### 3. Network Security Configuration

Configure Azure Network Security Groups:

```bash
# Allow HTTP/HTTPS to controller
az network nsg rule create \
  --resource-group px4-cloud-sim \
  --nsg-name px4-controller-nsg \
  --name AllowHTTP \
  --priority 1002 \
  --source-address-prefixes '*' \
  --destination-port-ranges 80 443 \
  --access Allow \
  --protocol Tcp

# Allow MAVLink UDP ports
az network nsg rule create \
  --resource-group px4-cloud-sim \
  --nsg-name px4-agent-nsg \
  --name AllowMAVLink \
  --priority 1006 \
  --source-address-prefixes '*' \
  --destination-port-ranges 14560-14570 \
  --access Allow \
  --protocol Udp
```

## Production Deployment

### 1. Security Considerations

- Use strong passwords and API keys
- Enable HTTPS with valid certificates
- Configure firewall rules properly
- Use Azure Key Vault for secrets
- Enable Azure Monitor and logging

### 2. High Availability

- Deploy controller behind Azure Load Balancer
- Use Azure Database for PostgreSQL (managed)
- Implement health checks and auto-scaling
- Set up backup and disaster recovery

### 3. Monitoring

```bash
# Install monitoring tools
sudo apt install -y prometheus-node-exporter

# Configure log aggregation
# Use Azure Monitor or ELK stack
```

### 4. SSL/TLS Configuration

```bash
# Using Let's Encrypt (recommended)
sudo apt install certbot
sudo certbot --nginx -d your-domain.com

# Or upload your own certificates
sudo cp your-cert.pem /etc/ssl/certs/
sudo cp your-key.pem /etc/ssl/private/
```

## Configuration

### Environment Variables

#### Controller (.env)
```bash
SECRET_KEY=your-secret-key-here
AGENT_API_KEY=agent-registration-key
DATABASE_URL=postgresql://user:pass@localhost/db
HOST=0.0.0.0
PORT=8000
DEBUG=false
ALLOWED_ORIGINS=["http://localhost:3000"]
```

#### Agent (.env)
```bash
CONTROLLER_URL=https://your-controller.com/api/v1/register
AGENT_API_KEY=agent-registration-key
NODE_ID=unique-node-id
NAME=Node Display Name
PUBLIC_ADDRESS=your-public-ip
PORT=8443
```

#### Frontend (.env)
```bash
REACT_APP_API_URL=https://your-controller.com
```

### Database Configuration

#### PostgreSQL (Production)
```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE px4_controller;
CREATE USER px4_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE px4_controller TO px4_user;
```

#### SQLite (Development)
```bash
# Default configuration uses SQLite
# Database file will be created automatically
```

## Troubleshooting

### Common Issues

#### 1. Agent Registration Failed
```bash
# Check agent logs
journalctl -u px4-agent -f

# Verify network connectivity
curl -k https://controller-ip:8000/health

# Check firewall rules
sudo ufw status
```

#### 2. PX4 Container Won't Start
```bash
# Check Docker status
docker ps -a
docker logs <container-id>

# Verify PX4 image
docker pull px4io/px4-dev-simulation:latest

# Check port availability
netstat -tulpn | grep 14560
```

#### 3. Frontend Can't Connect to API
```bash
# Check CORS configuration
# Verify API_URL in frontend .env
# Check browser developer tools for errors
```

#### 4. Database Connection Issues
```bash
# Test database connection
psql -h localhost -U px4_user -d px4_controller

# Check database logs
sudo tail -f /var/log/postgresql/postgresql-*.log
```

### Log Locations

- Controller logs: Check terminal output or systemd journal
- Agent logs: `journalctl -u px4-agent -f`
- Docker logs: `docker logs <container-name>`
- Nginx logs: `/var/log/nginx/`

### Performance Tuning

#### For Raspberry Pi (Limited Resources)
Based on user preferences, configure the system to:
- Start only single SITL instances per node
- Use smaller PX4 models (iris instead of x500)
- Limit concurrent instances
- Monitor resource usage

```bash
# Monitor system resources
htop
docker stats
```

### Getting Help

1. Check the logs first
2. Verify network connectivity
3. Ensure all services are running
4. Check firewall and security group rules
5. Review configuration files

For additional support, check the project documentation or create an issue in the repository.

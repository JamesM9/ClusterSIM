# PX4 Cloud Simulator - API Documentation

This document describes the REST API endpoints for the PX4 Cloud Simulator controller.

## Base URL

- Development: `http://localhost:8000`
- Production: `https://your-domain.com`

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

### Getting a Token

```bash
POST /auth/login
Content-Type: application/json

{
  "username": "your-username",
  "password": "your-password"
}
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

## Endpoints

### Authentication

#### Register User
```http
POST /auth/register
Content-Type: application/json

{
  "username": "newuser",
  "email": "user@example.com",
  "password": "securepassword"
}
```

#### Login
```http
POST /auth/login
Content-Type: application/json

{
  "username": "your-username",
  "password": "your-password"
}
```

### Nodes (Worker VMs)

#### List Nodes
```http
GET /api/v1/nodes
Authorization: Bearer <token>
```

Response:
```json
[
  {
    "id": "node-001",
    "name": "Azure VM 01",
    "address": "10.0.1.5",
    "tags": ["azure-vm", "px4-agent"],
    "last_seen": "2024-01-01T12:00:00Z",
    "status": "online",
    "cpu_cores": 4,
    "memory_gb": 16,
    "disk_gb": 50
  }
]
```

#### Get Node Details
```http
GET /api/v1/nodes/{node_id}
Authorization: Bearer <token>
```

#### Register Node (Agent Endpoint)
```http
POST /api/v1/register
Content-Type: application/json

{
  "node_id": "node-001",
  "name": "Azure VM 01",
  "address": "10.0.1.5",
  "tags": ["azure-vm", "px4-agent"],
  "api_key": "agent-registration-key",
  "cpu_cores": 4,
  "memory_gb": 16,
  "disk_gb": 50
}
```

### Instances

#### List Instances
```http
GET /api/v1/instances
Authorization: Bearer <token>
```

Response:
```json
[
  {
    "id": "inst-001",
    "node_id": "node-001",
    "container_id": "abc123def456",
    "name": "sim-iris-01",
    "vehicle_type": "copter",
    "model": "iris",
    "mav_udp": 14560,
    "status": "running",
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
  }
]
```

#### Get Instance Details
```http
GET /api/v1/instances/{instance_id}
Authorization: Bearer <token>
```

#### Start Instance
```http
POST /api/v1/nodes/{node_id}/start
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "my-simulation",
  "model": "iris",
  "vehicle_type": "copter",
  "mav_udp": 14560
}
```

Response:
```json
{
  "instance_id": "inst-001",
  "container_id": "abc123def456",
  "mav_udp": 14560,
  "status": "running"
}
```

#### Stop Instance
```http
POST /api/v1/nodes/{node_id}/stop
Authorization: Bearer <token>
Content-Type: application/json

{
  "instance_id": "inst-001"
}
```

Alternative:
```json
{
  "container_id": "abc123def456"
}
```

Response:
```json
{
  "status": "stopped",
  "container_id": "abc123def456",
  "instance_id": "inst-001"
}
```

### Health Check

#### Controller Health
```http
GET /health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## Agent API Endpoints

These endpoints are exposed by agents running on worker VMs:

### Agent Health
```http
GET https://agent-ip:8443/health
```

### Agent Status
```http
GET https://agent-ip:8443/agent/status
```

Response:
```json
{
  "node_id": "node-001",
  "name": "Azure VM 01",
  "status": "online",
  "running_instances": 2,
  "total_cpu_cores": 4,
  "total_memory_gb": 16,
  "total_disk_gb": 50,
  "available_ports": [14561, 14562, 14563]
}
```

### List Agent Instances
```http
GET https://agent-ip:8443/agent/instances
```

### Start Instance (Agent)
```http
POST https://agent-ip:8443/agent/start
Content-Type: application/json

{
  "name": "sim-iris-01",
  "model": "iris",
  "vehicle_type": "copter",
  "mav_udp": 14560
}
```

### Stop Instance (Agent)
```http
POST https://agent-ip:8443/agent/stop
Content-Type: application/json

{
  "instance_id": "inst-001"
}
```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 404 Not Found
```json
{
  "detail": "Node not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Failed to start instance: Docker error"
}
```

## Rate Limiting

The API implements rate limiting to prevent abuse:

- Authentication endpoints: 5 requests per minute
- Other endpoints: 100 requests per minute

When rate limited, you'll receive a 429 response:

```json
{
  "detail": "Rate limit exceeded"
}
```

## WebSocket Support (Future)

Planned WebSocket endpoints for real-time updates:

```javascript
// Connect to WebSocket
const ws = new WebSocket('wss://your-domain.com/ws');

// Listen for instance updates
ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  console.log('Instance update:', data);
};
```

## SDK Examples

### Python
```python
import requests

# Login
response = requests.post('http://localhost:8000/auth/login', json={
    'username': 'admin',
    'password': 'password'
})
token = response.json()['access_token']

# List nodes
headers = {'Authorization': f'Bearer {token}'}
response = requests.get('http://localhost:8000/api/v1/nodes', headers=headers)
nodes = response.json()

# Start instance
response = requests.post(
    f'http://localhost:8000/api/v1/nodes/{node_id}/start',
    json={'name': 'my-sim', 'model': 'iris'},
    headers=headers
)
```

### JavaScript/Node.js
```javascript
const axios = require('axios');

// Login
const loginResponse = await axios.post('http://localhost:8000/auth/login', {
  username: 'admin',
  password: 'password'
});
const token = loginResponse.data.access_token;

// List instances
const instancesResponse = await axios.get('http://localhost:8000/api/v1/instances', {
  headers: { Authorization: `Bearer ${token}` }
});
```

### cURL Examples
```bash
# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}'

# List nodes
curl -X GET http://localhost:8000/api/v1/nodes \
  -H "Authorization: Bearer YOUR_TOKEN"

# Start instance
curl -X POST http://localhost:8000/api/v1/nodes/node-001/start \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"my-sim","model":"iris"}'
```

## MAVLink Connection

Once an instance is running, you can connect to it using QGroundControl or other MAVLink clients:

1. **QGroundControl**: Use the UDP connection with the agent's public IP and the MAVLink port
2. **MAVProxy**: `mavproxy.py --master=udp:agent-ip:mavlink-port`
3. **Custom applications**: Connect to the UDP port exposed by the container

Example QGroundControl connection:
- Connection Type: UDP
- Host: `agent-public-ip`
- Port: `14560` (or the port returned by the start instance API)

## Security Considerations

1. **API Keys**: Use strong, unique API keys for agent registration
2. **JWT Tokens**: Tokens expire after 30 minutes by default
3. **HTTPS**: Always use HTTPS in production
4. **Network Security**: Restrict agent API access to controller IPs only
5. **Input Validation**: All inputs are validated and sanitized

## Versioning

The API uses URL versioning: `/api/v1/`. Future versions will use `/api/v2/`, etc.

Breaking changes will be communicated in advance with migration guides.

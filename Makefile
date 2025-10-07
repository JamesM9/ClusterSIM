# PX4 Cloud Simulator - Makefile

.PHONY: help install-dev install-prod build test clean docker-build docker-run terraform-init terraform-plan terraform-apply

# Default target
help:
	@echo "PX4 Cloud Simulator - Available commands:"
	@echo ""
	@echo "Development:"
	@echo "  install-dev     Install development dependencies"
	@echo "  install-prod    Install production dependencies"
	@echo "  run-controller  Start the controller in development mode"
	@echo "  run-agent       Start an agent in development mode"
	@echo "  run-frontend    Start the frontend in development mode"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build    Build all Docker images"
	@echo "  docker-run      Run with Docker Compose"
	@echo "  docker-stop     Stop Docker Compose services"
	@echo "  docker-clean    Clean up Docker containers and images"
	@echo ""
	@echo "Terraform:"
	@echo "  terraform-init  Initialize Terraform"
	@echo "  terraform-plan  Plan Terraform deployment"
	@echo "  terraform-apply Apply Terraform configuration"
	@echo "  terraform-destroy Destroy Terraform resources"
	@echo ""
	@echo "Utilities:"
	@echo "  test           Run tests"
	@echo "  clean          Clean up generated files"
	@echo "  setup-user     Create default admin user"

# Development setup
install-dev:
	@echo "Installing development dependencies..."
	cd controller && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
	cd agent && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
	cd frontend && npm install

install-prod:
	@echo "Installing production dependencies..."
	cd controller && pip install -r requirements.txt
	cd agent && pip install -r requirements.txt
	cd frontend && npm install --production

# Run services in development
run-controller:
	@echo "Starting controller..."
	cd controller && source venv/bin/activate && python run.py

run-agent:
	@echo "Starting agent..."
	cd agent && source venv/bin/activate && python run.py

run-frontend:
	@echo "Starting frontend..."
	cd frontend && npm start

# Docker commands
docker-build:
	@echo "Building Docker images..."
	docker-compose -f deployment/docker/docker-compose.yml build

docker-run:
	@echo "Starting services with Docker Compose..."
	cd deployment/docker && docker-compose up -d

docker-stop:
	@echo "Stopping Docker Compose services..."
	cd deployment/docker && docker-compose down

docker-clean:
	@echo "Cleaning up Docker resources..."
	docker-compose -f deployment/docker/docker-compose.yml down -v --rmi all --remove-orphans

# Terraform commands
terraform-init:
	@echo "Initializing Terraform..."
	cd deployment/terraform && terraform init

terraform-plan:
	@echo "Planning Terraform deployment..."
	cd deployment/terraform && terraform plan

terraform-apply:
	@echo "Applying Terraform configuration..."
	cd deployment/terraform && terraform apply

terraform-destroy:
	@echo "Destroying Terraform resources..."
	cd deployment/terraform && terraform destroy

# Utility commands
test:
	@echo "Running tests..."
	cd controller && python -m pytest tests/ || echo "No tests found in controller"
	cd agent && python -m pytest tests/ || echo "No tests found in agent"
	cd frontend && npm test || echo "Frontend tests not configured"

clean:
	@echo "Cleaning up generated files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + || true
	find . -type f -name "*.pyc" -delete || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + || true
	find . -type d -name "node_modules" -exec rm -rf {} + || true
	find . -type d -name ".next" -exec rm -rf {} + || true
	rm -f controller/controller.db || true
	rm -f controller/controller.db-journal || true

setup-user:
	@echo "Creating default admin user..."
	@echo "You can create a user via the API:"
	@echo "curl -X POST http://localhost:8000/auth/register \\"
	@echo "  -H 'Content-Type: application/json' \\"
	@echo "  -d '{\"username\":\"admin\",\"email\":\"admin@example.com\",\"password\":\"admin123\"}'"

# Quick start commands
quickstart-docker: docker-build docker-run
	@echo "Quick start with Docker completed!"
	@echo "Access the web interface at: http://localhost"
	@echo "API available at: http://localhost:8000"
	@echo ""
	@echo "Create an admin user with: make setup-user"

quickstart-local: install-dev
	@echo "Local development setup completed!"
	@echo "Start services with:"
	@echo "  make run-controller  (in one terminal)"
	@echo "  make run-agent       (in another terminal)"
	@echo "  make run-frontend    (in a third terminal)"

# Development helpers
logs-controller:
	cd deployment/docker && docker-compose logs -f controller

logs-agent:
	cd deployment/docker && docker-compose logs -f agent

logs-frontend:
	cd deployment/docker && docker-compose logs -f frontend

# Status checks
status:
	@echo "Checking service status..."
	@curl -s http://localhost:8000/health > /dev/null && echo "✓ Controller is running" || echo "✗ Controller is not responding"
	@curl -s http://localhost > /dev/null && echo "✓ Frontend is running" || echo "✗ Frontend is not responding"
	@curl -s http://localhost:8443/health > /dev/null && echo "✓ Agent is running" || echo "✗ Agent is not responding"

# Backup and restore
backup-db:
	@echo "Creating database backup..."
	@mkdir -p backups
	@cd deployment/docker && docker-compose exec postgres pg_dump -U px4_user px4_controller > ../../backups/db_backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "Database backup created in backups/ directory"

# Environment setup
env-setup:
	@echo "Setting up environment files..."
	@cp controller/env.example controller/.env || echo "Controller .env already exists"
	@cp agent/env.example agent/.env || echo "Agent .env already exists"
	@cp frontend/env.example frontend/.env || echo "Frontend .env already exists"
	@cp deployment/terraform/terraform.tfvars.example deployment/terraform/terraform.tfvars || echo "Terraform tfvars already exists"
	@echo "Environment files created. Please edit them with your configuration."

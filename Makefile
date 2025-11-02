# Makefile - Simple commands to manage your Docker containers
# Usage: Just type "make <command>" in your terminal
# Example: make up, make down, make logs, etc.

.PHONY: help up down restart logs logs-backend logs-frontend build clean status shell-backend shell-frontend

# Default command when you just type "make"
help:
	@echo "Available commands:"
	@echo "  make up              - Start both frontend and backend containers"
	@echo "  make down            - Stop and remove all containers"
	@echo "  make restart         - Restart all containers"
	@echo "  make build           - Rebuild containers from scratch"
	@echo "  make logs            - Show logs from all containers"
	@echo "  make logs-backend    - Show only backend logs"
	@echo "  make logs-frontend   - Show only frontend logs"
	@echo "  make status          - Show status of all containers"
	@echo "  make clean           - Remove containers, networks, and volumes"
	@echo "  make shell-backend   - Open a shell inside the backend container"
	@echo "  make shell-frontend  - Open a shell inside the frontend container"

# Start the application (builds images if needed, then starts containers)
up:
	@echo "Starting the application..."
	docker-compose up -d
	@echo ""
	@echo "Application is running!"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend:  http://localhost:43798"
	@echo ""
	@echo "Run 'make logs' to see container logs"

# Stop and remove containers
down:
	@echo "Stopping the application..."
	docker-compose down

# Restart all containers
restart:
	@echo "Restarting the application..."
	docker-compose restart

# Rebuild containers from scratch (useful when you change Dockerfile or dependencies)
build:
	@echo "Rebuilding containers..."
	docker-compose build --no-cache

# Show logs from all containers (press Ctrl+C to exit)
logs:
	docker-compose logs -f

# Show only backend logs
logs-backend:
	docker-compose logs -f backend

# Show only frontend logs
logs-frontend:
	docker-compose logs -f frontend

# Show status of containers
status:
	docker-compose ps

# Clean up everything (containers, networks, volumes)
clean:
	@echo "Cleaning up Docker resources..."
	docker-compose down -v --remove-orphans
	@echo "Cleanup complete!"

# Open a bash shell inside the backend container
shell-backend:
	docker-compose exec backend /bin/bash

# Open a shell inside the frontend container
shell-frontend:
	docker-compose exec frontend /bin/sh

# Quick start: build and run
start: build up

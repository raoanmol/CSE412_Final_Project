# Makefile - Simple commands to manage your Docker containers
# Usage: Just type "make <command>" in your terminal
# Example: make up, make down, make logs, etc.

.PHONY: help up down restart logs logs-backend logs-frontend logs-db build clean status shell-backend shell-frontend shell-db db-load db-load-students db-load-all db-connect db-reset

# Default command when you just type "make"
help:
	@echo "Available commands:"
	@echo "  make up              - Start all containers (frontend, backend, database)"
	@echo "  make down            - Stop and remove all containers"
	@echo "  make restart         - Restart all containers"
	@echo "  make build           - Rebuild containers from scratch"
	@echo "  make logs            - Show logs from all containers"
	@echo "  make logs-backend    - Show only backend logs"
	@echo "  make logs-frontend   - Show only frontend logs"
	@echo "  make logs-db         - Show only database logs"
	@echo "  make status          - Show status of all containers"
	@echo "  make clean           - Remove containers, networks, and volumes"
	@echo "  make shell-backend   - Open a shell inside the backend container"
	@echo "  make shell-frontend  - Open a shell inside the frontend container"
	@echo "  make shell-db        - Open a psql shell inside the database container"
	@echo "  make db-load         - Manually load scraped events data"
	@echo "  make db-load-students- Manually generate and load student data (5000 students)"
	@echo "  make db-load-all     - Manually load events and students"
	@echo "  make db-connect      - Connect to the database with psql"
	@echo "  make db-reset        - Reset database (WARNING: deletes all data)"
	@echo ""
	@echo "Note: Events and students are auto-loaded on first 'make up' if database is empty"

# Start the application (builds images if needed, then starts containers)
up:
	@echo "Starting the application..."
	docker-compose up -d
	@echo ""
	@echo "Application is running!"
	@echo "Frontend:  http://localhost:3000"
	@echo "Backend:   http://localhost:43798"
	@echo "Database:  http://localhost:5432"
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

# Show only database logs
logs-db:
	docker-compose logs -f db

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

# Open a psql shell inside the database container
shell-db:
	docker-compose exec db psql -U postgres -d asu_events

# Load scraped events data into the database
db-load:
	@echo "Loading events data into database..."
	docker-compose exec backend python /database/load_data.py

# Generate and load student data into the database
db-load-students:
	@echo "Generating and loading student data into database..."
	docker-compose exec backend python /database/generate_students.py

# Load all data (events + students)
db-load-all: db-load db-load-students
	@echo "All data loaded successfully!"

# Connect to the database with psql
db-connect:
	@echo "Connecting to database..."
	docker-compose exec db psql -U postgres -d asu_events

# Reset the database (WARNING: deletes all data)
db-reset:
	@echo "WARNING: This will delete all data in the database!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "Resetting database..."; \
		docker-compose exec db psql -U postgres -d asu_events -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"; \
		docker-compose restart db; \
		echo "Database reset complete. Run 'make db-load' to reload data."; \
	else \
		echo "Database reset cancelled."; \
	fi

# Quick start: build and run
start: build up

.PHONY: help setup run convert pull-model clean build logs stop restart

help:
	@echo "MyFiles to Markdown - Makefile Commands"
	@echo ""
	@echo "Available commands:"
	@echo "  make setup       - Initial setup (first time)"
	@echo "  make convert     - Convert a single file (pass FILE=path/to/file)"
	@echo "  make run         - Batch convert (input/ directory)"
	@echo "  make build       - Build Docker containers"
	@echo "  make logs        - View live logs"
	@echo "  make stop        - Stop all services"
	@echo "  make restart     - Restart services"
	@echo "  make clean       - Clean output and logs"
	@echo "  make pull-model  - Pull Ollama model"
	@echo ""
	@echo "Examples:"
	@echo "  make convert FILE=document.pdf"
	@echo "  make convert FILE=~/Documents/report.docx"
	@echo ""

setup:
	@echo "Running setup..."
	@./scripts/setup.sh

convert:
	@if [ -z "$(FILE)" ]; then \
		echo "Error: FILE not specified"; \
		echo "Usage: make convert FILE=path/to/file"; \
		exit 1; \
	fi
	@echo "Converting file: $(FILE)"
	@./convert.sh "$(FILE)"

run:
	@echo "Starting batch conversion..."
	@docker compose up converter

run-detached:
	@echo "Starting batch conversion in background..."
	@docker compose up -d converter

build:
	@echo "Building Docker containers..."
	@docker compose build

logs:
	@echo "Showing logs (Ctrl+C to exit)..."
	@docker compose logs -f

logs-converter:
	@echo "Showing converter logs (Ctrl+C to exit)..."
	@docker compose logs -f converter

logs-ollama:
	@echo "Showing Ollama logs (Ctrl+C to exit)..."
	@docker compose logs -f ollama

stop:
	@echo "Stopping services..."
	@docker compose down

restart:
	@echo "Restarting services..."
	@docker compose restart

clean:
	@echo "Cleaning up..."
	@./scripts/clean.sh

pull-model:
	@echo "Pulling default model..."
	@./scripts/pull_model.sh llama3.2:latest

status:
	@echo "Service status:"
	@docker compose ps

test:
	@echo "Testing setup..."
	@docker compose config
	@echo "✓ Configuration is valid"


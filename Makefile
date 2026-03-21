# Variables
DC := docker compose
UV := uv

.PHONY: help setup sync clean-local up build down restart logs logs-api logs-ui clean-docker lint format

.DEFAULT_GOAL := help

help:
	@python -c "print('\nUsage:\n  make <target>\n\nLocal Environment:\n  setup           Initialize virtual environment\n  sync            Sync dependencies\n  clean-local     Remove virtual environment and cache files\n\nDocker Orchestration:\n  up              Start Docker services\n  build           Build Docker images\n  down            Stop Docker services\n  restart         Restart Docker services\n  logs            Tail logs for all services\n  logs-api        Tail API logs\n  logs-ui         Tail UI logs\n  clean-docker    Remove containers, volumes, and orphans\n\nQuality Assurance:\n  lint            Run Ruff linter\n  format          Run Ruff formatter\n')"

setup:
	$(UV) venv
	$(UV) sync

sync:
	$(UV) sync

clean-local:
	@python -c "import os, shutil; [shutil.rmtree(d, ignore_errors=True) for d in ['.venv', '.pytest_cache', '.ruff_cache']]; [shutil.rmtree(os.path.join(r, d), ignore_errors=True) for r, dirs, f in os.walk('.') for d in dirs if d == '__pycache__']; [os.remove(f) for f in ['uv.lock'] if os.path.exists(f)]"
	@echo Local environment cleaned.

up:
	$(DC) up -d

build:
	$(DC) build --no-cache

down:
	$(DC) down

restart: down up

logs:
	$(DC) logs -f

logs-api:
	$(DC) logs -f backend

logs-ui:
	$(DC) logs -f frontend

clean-docker:
	$(DC) down -v --remove-orphans

lint:
	$(UV) run ruff check .

format:
	$(UV) run ruff format .

test:
	$(UV) run pytest -v tests/
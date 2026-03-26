# Variables
DC := docker compose
UV := uv
KUBECTL := kubectl
HELM := helm

.PHONY: help setup sync clean-local up build down restart logs logs-api logs-ui clean-docker lint format test k8s-deploy k8s-forward k8s-delete gitops-apply

.DEFAULT_GOAL := help

help:
	@echo "Usage: make <target>"
	@echo ""
	@echo "Local Environment (Python/UV):"
	@echo "  setup           Initialize virtual environment"
	@echo "  sync            Sync dependencies"
	@echo "  clean-local     Remove virtual environment and cache files"
	@echo "  lint            Run Ruff linter"
	@echo "  format          Run Ruff formatter"
	@echo "  test            Run pytest"
	@echo ""
	@echo "Local Orchestration (Docker Compose):"
	@echo "  build           Build Docker images"
	@echo "  up              Start Docker services"
	@echo "  down            Stop Docker services"
	@echo "  clean-docker    Remove containers, volumes, and orphans"
	@echo ""
	@echo "Cloud/Production Orchestration (Kubernetes & GitOps):"
	@echo "  k8s-deploy      Deploy the application using Helm"
	@echo "  k8s-forward     Port-forward the frontend service to localhost:8501"
	@echo "  k8s-delete      Uninstall the Helm release from the cluster"
	@echo "  gitops-apply    Apply the ArgoCD application manifest"

setup:
	$(UV) venv
	$(UV) sync

sync:
	$(UV) sync

clean-local:
	@python -c "import os, shutil; [shutil.rmtree(d, ignore_errors=True) for d in ['.venv', '.pytest_cache', '.ruff_cache']]; [shutil.rmtree(os.path.join(r, d), ignore_errors=True) for r, dirs, f in os.walk('.') for d in dirs if d == '__pycache__']; [os.remove(f) for f in ['uv.lock'] if os.path.exists(f)]"
	@echo Local environment cleaned.

# --- Docker Compose Commands ---
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

# --- Quality Assurance ---
lint:
	$(UV) run ruff check .

format:
	$(UV) run ruff format .

test:
	$(UV) run pytest -v tests/

# --- Kubernetes & Helm Commands ---
k8s-deploy:
	$(HELM) upgrade --install lumiere ./helm/lumiere --namespace default

k8s-forward:
	@echo "Forwarding port 8501. Press Ctrl+C to stop."
	$(KUBECTL) port-forward svc/lumiere-frontend 8501:8501

k8s-delete:
	$(HELM) uninstall lumiere --namespace default

# --- GitOps Commands ---
gitops-apply:
	$(KUBECTL) apply -f helm/argocd-app.yaml
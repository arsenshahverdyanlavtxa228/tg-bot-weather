.PHONY: help install dev run lint fmt typecheck test cov clean docker-build docker-up docker-down

PYTHON ?= python3
VENV ?= .venv
BIN = $(VENV)/bin

help:
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

$(VENV):
	$(PYTHON) -m venv $(VENV)
	$(BIN)/pip install --upgrade pip

install: $(VENV)  ## Install runtime deps
	$(BIN)/pip install -e .

dev: $(VENV)  ## Install runtime + dev deps
	$(BIN)/pip install -e ".[dev]"

run:  ## Run the bot locally (reads .env)
	$(BIN)/python -m bot

lint:  ## Ruff lint
	$(BIN)/ruff check src tests

fmt:  ## Ruff format + auto-fix
	$(BIN)/ruff format src tests
	$(BIN)/ruff check --fix src tests

typecheck:  ## Mypy type checking
	$(BIN)/mypy src

test:  ## Run tests
	$(BIN)/pytest

cov:  ## Tests with HTML coverage
	$(BIN)/pytest --cov=bot --cov-report=html

clean:  ## Clean caches
	rm -rf build dist *.egg-info .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +

docker-build:  ## Build docker image
	docker build -t tg-bot-weather:latest .

docker-up:  ## Start via docker compose
	docker compose up -d --build

docker-down:  ## Stop docker compose
	docker compose down

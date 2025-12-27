PYTHON ?= python3
VENV ?= .venv
ACTIVATE = . $(VENV)/bin/activate

.PHONY: install lint test build local format clean

install:
	$(PYTHON) -m venv $(VENV)
	$(ACTIVATE) && pip install --upgrade pip
	$(ACTIVATE) && pip install -e .[dev]

lint:
	$(ACTIVATE) && ruff .
	$(ACTIVATE) && black --check .
	$(ACTIVATE) && mypy src

format:
	$(ACTIVATE) && black .

test:
	$(ACTIVATE) && pytest

build:
	$(ACTIVATE) && sam build

local:
	$(ACTIVATE) && ./scripts/run_local.sh

clean:
	rm -rf $(VENV) .aws-sam .pytest_cache .mypy_cache dist build

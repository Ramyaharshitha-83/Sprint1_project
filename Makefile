PYTHON ?= python3

.PHONY: help setup install test

help:
	@echo "Available targets:"
	@echo "  setup        - create a virtual environment and install dependencies"
	@echo "  install      - install Python dependencies"
	@echo "  test         - run tests"

setup:
	$(PYTHON) -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt

install:
	. .venv/bin/activate && pip install -r requirements.txt

test:
	. .venv/bin/activate && pytest -q

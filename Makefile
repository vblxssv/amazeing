# Переменные
PYTHON_SYS = python3
VENV = .venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip3
MAIN_SCRIPT = a_maze_ing.py
CONFIG = config.txt
PACKAGE_NAME = mazegen

.PHONY: all install run debug clean lint lint-strict build venv

all: venv lint build

venv:
	@if [ ! -d "$(VENV)" ]; then \
		$(PYTHON_SYS) -m venv $(VENV); \
		$(PIP) install --upgrade pip; \
		$(PIP) install mlx flake8 mypy build; \
		echo "Virtual environment created and dependencies installed."; \
	fi

install: venv

run: venv
	$(PYTHON) $(MAIN_SCRIPT) $(CONFIG)

debug: venv
	$(PYTHON) -m pdb $(MAIN_SCRIPT) $(CONFIG)

clean:
	rm -rf $(VENV)
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} +

lint: venv
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict: venv
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy . --strict

build: venv
	$(PYTHON) -m build
	cp dist/*.whl .
	@echo "Build complete. Wheel file is in the root directory."
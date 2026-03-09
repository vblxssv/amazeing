# Variables
PYTHON_SYS   := python3
VENV         := .venv
PYTHON       := $(VENV)/bin/python3
PIP          := $(VENV)/bin/pip
MAIN_SCRIPT  := a_maze_ing.py
CONFIG       := config.txt

INFO := @echo "\033[32m[INFO]\033[0m"

.PHONY: all venv install run clean lint lint-strict build test-install

all: install lint build

$(VENV)/bin/activate: requirements.txt
	$(INFO) "Creating virtual environment and installing dependencies..."
	$(PYTHON_SYS) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PIP) install build wheel  # Гарантируем наличие инструментов сборки
	@touch $(VENV)/bin/activate

venv: $(VENV)/bin/activate

install: venv

run: venv
	@$(PYTHON) $(MAIN_SCRIPT) $(CONFIG)

debug: venv
	$(PYTHON) -m pdb $(MAIN_SCRIPT) $(CONFIG)

clean:
	$(INFO) "Cleaning up workspace..."
	rm -rf $(VENV) dist build *.egg-info .mypy_cache .pytest_cache *.whl
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

lint: venv
	$(INFO) "Running flake8 and mypy..."
	$(PYTHON) -m flake8 . --exclude=$(VENV),build,dist
	$(PYTHON) -m mypy . --exclude $(VENV) --ignore-missing-imports --disallow-untyped-defs

lint-strict: venv
	$(PYTHON) -m flake8 . --exclude=$(VENV),build,dist
	$(PYTHON) -m mypy . --exclude $(VENV) --strict

build: venv
	$(INFO) "Starting build process..."
	@rm -rf dist build *.egg-info
	@$(PYTHON) -m build
	@cp dist/*.whl .
	@rm -rf dist build *.egg-info
	$(INFO) "Success: Wheel file is at the root. Temporary folders removed."

test-install: build
	$(INFO) "Verifying installation from wheel..."
	$(PIP) install --force-reinstall *.whl
	$(INFO) "Package installed successfully. You can now import MazeGenerator anywhere."
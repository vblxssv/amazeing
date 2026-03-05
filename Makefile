# Переменные
PYTHON = python3
PIP = pip3
MAIN_SCRIPT = a_maze_ing.py
CONFIG = config.txt
PACKAGE_NAME = mazegen

.PHONY: all install run debug clean lint lint-strict build

all: lint build

# III.2: Install project dependencies
install:
	$(PIP) install --upgrade pip
	$(PIP) install flake8 mypy build

# III.2: Execute the main script
run:
	$(PYTHON) $(MAIN_SCRIPT) $(CONFIG)

# III.2: Run the main script in debug mode (using pdb)
debug:
	$(PYTHON) -m pdb $(MAIN_SCRIPT) $(CONFIG)

# III.2: Remove temporary files or caches
clean:
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} +

# III.2: Mandatory lint with specific flags
lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

# III.2: Optional strict lint
lint-strict:
	flake8 .
	mypy . --strict

# Дополнительное правило для сборки .whl пакета (Chapter VI)
build:
	$(PYTHON) -m build
	cp dist/*.whl .
	@echo "Build complete. Wheel file is in the root directory."
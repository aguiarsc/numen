.PHONY: install dev-install test lint format clean

install:
	pip install -e .

dev-install:
	pip install -e ".[dev]"

test:
	pytest

lint:
	black src tests
	isort src tests
	mypy src

format:
	black src tests
	isort src tests

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete 
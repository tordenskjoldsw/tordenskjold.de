# Keep verify output readable even when make runs with -j.
.NOTPARALLEL:

.PHONY: install dev format format-check lint typecheck test verify

install:
	uv sync
	uv run pre-commit install

dev:
	uv run uvicorn portfolio.main:app --reload

format:
	uv run ruff format .

format-check:
	uv run ruff format --check .

lint:
	uv run ruff check .

typecheck:
	uv run mypy

test:
	uv run pytest

verify: format-check lint typecheck test

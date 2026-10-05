# Keep verify output readable even when make runs with -j.
.NOTPARALLEL:

.PHONY: install dev format format-check lint typecheck test verify

install:
	uv sync
	uv run pre-commit install

# Content and static file hashes are read at startup, so changes to them
# need a restart as well.
dev:
	uv run uvicorn portfolio.main:app --reload \
		--reload-include '*.css' --reload-include '*.md' --reload-include '*.yaml'

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

.PHONY: install hooks run log format lint lint-fix test clean

install:
	uv sync
	@$(MAKE) hooks

hooks:
	git config core.hooksPath .githooks

run:
	PYTHONPATH=src uv run python src/main.py

log:
	PYTHONPATH=src uv run python src/cli.py "$(MSG)" $(if $(TYPE),--type $(TYPE),)

format:
	uv run ruff format .

lint:
	uv run ruff check .

lint-fix:
	uv run ruff check --fix .

test:
	PYTHONPATH=src uv run pytest

clean:
	find . -type d -name '__pycache__' -not -path './.venv/*' -exec rm -rf {} +
	rm -rf .ruff_cache .pytest_cache

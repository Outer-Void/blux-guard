.PHONY: dev lint test tui smoke

dev:
	python -m pip install -U pip && pip install -e .[dev] || pip install -e .
	pip install ruff mypy pytest

lint:
	ruff check .
	mypy blux_guard || true

test:
	pytest

tui:
	bluxq guard tui --mode dev

smoke:
	python -c "import blux_guard"
	python -m blux_guard.cli.bluxq --help

.PHONY: dev lint test tui filetree

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

filetree:
	python scripts/update_readme_filetree.py

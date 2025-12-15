.PHONY: dev lint test tui perms audit-scripts smoke

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

perms:
        bash scripts/fix_perms.sh

audit-scripts:
        python scripts/audit_scripts.py

smoke: audit-scripts
        python -c "import blux_guard"
        python -m blux_guard.cli.bluxq --help
        bash scripts/fix_perms.sh --check

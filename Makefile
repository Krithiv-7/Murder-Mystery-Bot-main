.PHONY: install test lint format run docker

install:
	python -m pip install -r requirements.txt pytest ruff mypy

test:
	python -m pytest -q

lint:
	python -m ruff check core/manager.py core/ids.py core/lobby.py core/commands_meta.py core/cli.py core/runtime.py core/version.py storage/sqlite_store.py scripts/migrate.py
	python -m mypy

format:
	python -m ruff check --fix core/manager.py core/ids.py core/lobby.py core/commands_meta.py core/cli.py core/runtime.py storage/sqlite_store.py

run:
	python bot.py

docker:
	docker compose up -d

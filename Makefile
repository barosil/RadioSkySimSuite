# RadioSkySim Makefile
#
# O projeto é um uv workspace (AGENTS.md). O .venv é criado/gerido pelo uv,
# que NÃO instala pip por padrão — por isso os targets de ambiente usam `uv`.
#
# Targets:
#   make setup          # uv sync (cria .venv + deps + pacote editable)
#   make install        # uv sync no .venv existente
#   make install-extra  # instala dependências extras (requirements_extra.txt)
#   make postgres-up    # sobe postgres + adminer + backup (docker compose)
#   make postgres-down  # derruba os containers
#   make postgres-logs  # acompanha os logs
#   make postgres-restart# reinicia os containers
#   make postgres-reset # derruba e sobe de novo (dados preservados em data/DB)
#   make postgres-psql  # abre psql no container
#   make test           # roda a suíte pytest
#   make lint           # roda ruff (check + format --check)
#   make format         # aplica ruff format + fix
#   make docs           # builda a documentação Sphinx
#   make clean          # remove __pycache__, build artifacts
#   make help           # lista os targets

SHELL := /bin/bash
PYTHON ?= python3
VENV := .venv
UV ?= uv
PY := $(VENV)/bin/python
COMPOSE_DIR := docker/postgresql
COMPOSE := docker compose
ENV_FILE := $(COMPOSE_DIR)/.env

# ── Help ────────────────────────────────────────────────────────────
.PHONY: help
help:
	@echo "RadioSkySim Makefile"
	@echo "---------------------"
	@grep -E '^[a-zA-Z_-]+:.*# ' $(MAKEFILE_LIST) | sed 's/:.*# /  /' | sort

# ── Ambiente Python (uv workspace) ────────────────────────────────
.PHONY: setup
setup:   ## Cria/sincroniza o .venv via uv sync (deps + pacote editable)
	$(UV) sync --extra test --extra dev --extra docs
	@echo "Setup concluído. Ative com: source $(VENV)/bin/activate"

.PHONY: install
install:   ## Sincroniza o workspace no .venv existente
	$(UV) sync --extra test --extra dev --extra docs
	@echo "Instalação concluída."

.PHONY: install-extra
install-extra:   ## Instala dependências extras (opcional)
	$(UV) pip install --python $(PY) -r requirements_extra.txt
	@echo "Extras instalados."

# ── PostgreSQL (Docker) ─────────────────────────────────────────────
$(ENV_FILE):
	@echo "Gerando $(ENV_FILE) com valores padrão..."
	@printf 'POSTGRES_USER=radio\nPOSTGRES_PASSWORD=radio\nPOSTGRES_DB=radioskysims\nPOSTGRES_PORT=5432\n' > $(ENV_FILE)
	@echo "Edite $(ENV_FILE) se necessário."

.PHONY: postgres-env
postgres-env: $(ENV_FILE)   ## Cria o .env do compose com valores padrão

.PHONY: postgres-up
postgres-up: $(ENV_FILE)   ## Sobe postgres + adminer + backup
	cd $(COMPOSE_DIR) && $(COMPOSE) up -d
	@echo "Postgres pronto. Adminer: http://localhost:8080"

.PHONY: postgres-down
postgres-down:   ## Derruba os containers
	cd $(COMPOSE_DIR) && $(COMPOSE) down

.PHONY: postgres-logs
postgres-logs:   ## Acompanha os logs dos containers
	cd $(COMPOSE_DIR) && $(COMPOSE) logs -f

.PHONY: postgres-restart
postgres-restart: postgres-down postgres-up   ## Reinicia os containers

.PHONY: postgres-reset
postgres-reset:   ## Derruba e sobe (volume data/DB preservado)
	cd $(COMPOSE_DIR) && $(COMPOSE) down
	cd $(COMPOSE_DIR) && $(COMPOSE) up -d

.PHONY: postgres-psql
postgres-psql:   ## Abre psql no container postgres
	cd $(COMPOSE_DIR) && $(COMPOSE) exec postgres psql -U $${POSTGRES_USER:-radio} -d $${POSTGRES_DB:-radioskysims}

.PHONY: postgres-status
postgres-status:   ## Status dos containers e healthcheck
	cd $(COMPOSE_DIR) && $(COMPOSE) ps

# ── Qualidade ───────────────────────────────────────────────────────
.PHONY: test
test:   ## Roda a suíte pytest
	$(UV) run pytest tests/ -q

.PHONY: lint
lint:   ## Roda ruff check + format --check
	$(UV) run ruff check src/ tests/ scripts/ packages/*/src
	$(UV) run ruff format --check src/ tests/ scripts/ packages/*/src

.PHONY: format
format:   ## Aplica ruff format + fix
	$(UV) run ruff format src/ tests/ scripts/ packages/*/src
	$(UV) run ruff check --fix src/ tests/ scripts/ packages/*/src

# ── Documentação ───────────────────────────────────────────────────
.PHONY: docs
docs:   ## Builda a documentação Sphinx
	cd docs && make html

# ── Limpeza ────────────────────────────────────────────────────────
.PHONY: clean
clean:   ## Remove __pycache__ e artefatos de build
	find . -type d -name "__pycache__" -not -path "./.venv/*" -not -path "./data/*" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build dist .pytest_cache .ruff_cache
	rm -rf docs/source/_build
	@echo "Limpeza concluída."

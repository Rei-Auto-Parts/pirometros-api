SHELL := /bin/bash
COMPOSE ?= docker compose
DEV ?= dev
EXEC := $(COMPOSE) exec -T $(DEV)
COVERAGE_MIN ?= 90
ARG = $(filter-out $@,$(MAKECMDGOALS))

.PHONY: infra install init fmt lint test cover it bdd validate run down ps logs help
.DEFAULT_GOAL := help

%:
	@:

help: ## lista os alvos do contrato de operacao
	@grep -E '^[a-z-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  %-10s %s\n", $$1, $$2}'

infra: ## builda a imagem e sobe todos os servicos do compose
	$(COMPOSE) build
	$(COMPOSE) up -d

install: ## instala dependencias dentro do servico dev
	$(EXEC) pip install --no-cache-dir -e ".[dev]"

init: ## inicializa a infraestrutura local
	$(EXEC) python3 scripts/init_infra.py

fmt: ## formata o codigo
	$(EXEC) black $(if $(ARG),$(ARG),.)
	$(EXEC) ruff check --fix $(if $(ARG),$(ARG),.)

lint: ## analise estatica
	$(EXEC) ruff check $(if $(ARG),$(ARG),.)
	$(EXEC) mypy $(if $(ARG),$(ARG),.)

test: ## testes unitarios
	$(EXEC) pytest $(if $(ARG),tests/unit/$(ARG),tests/unit)

cover: ## cobertura em HTML com portao minimo
	$(EXEC) pytest tests/unit --cov --cov-report=html --cov-report=term
	$(EXEC) sh -c "coverage report | tail -1" | python3 scripts/coverage_gate.py --min $(COVERAGE_MIN)

it: ## testes de integracao
	$(EXEC) pytest $(if $(ARG),tests/it/$(ARG),tests/it)

bdd: ## testes BDD
	$(EXEC) behave tests/bdd

validate: ## pipeline completa de qualidade
	$(MAKE) fmt && $(MAKE) lint && $(MAKE) test && $(MAKE) cover && $(MAKE) it && $(MAKE) bdd

run: ## executa a aplicacao dentro do servico dev
	$(EXEC) python3 main.py

down: ## derruba os containers
	$(COMPOSE) down $(ARG)

ps: ## lista os servicos em execucao
	$(COMPOSE) ps

logs: ## acompanha os logs
	$(COMPOSE) logs -f $(ARG)

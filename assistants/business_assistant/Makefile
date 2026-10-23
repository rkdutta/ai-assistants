# Config-driven: what this assistant needs (model, MCP, RAG, db, api) is
# declared in assistant.yaml and run by library/runtime/run.py, which skips
# anything not declared. Other targets (venv, build, ...) go to the root Makefile.

ROOT := ../..
ROOT_ABS := $(abspath $(ROOT))
WORKING_DIR := $(patsubst $(ROOT_ABS)/%,%,$(CURDIR))
RUN := cd $(ROOT) && WORKING_DIR=$(WORKING_DIR) .venv/bin/python -m library.runtime.run

.PHONY: db rag api start bootstrap vars

vars: ## Print the variables this Makefile computes
	@echo "ROOT        = $(ROOT)"
	@echo "ROOT_ABS    = $(ROOT_ABS)"
	@echo "CURDIR      = $(CURDIR)"
	@echo "WORKING_DIR = $(WORKING_DIR)"
	@echo "RUN         = $(RUN)"

db rag api:
	$(RUN) $@

start:
	$(MAKE) -C $(ROOT) build
	$(RUN) start

bootstrap:
	$(MAKE) -C $(ROOT) venv
	$(MAKE) start

%:
	$(MAKE) -C $(ROOT) $@ WORKING_DIR=$(WORKING_DIR)

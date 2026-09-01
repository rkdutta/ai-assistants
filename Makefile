VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
STREAMLIT := $(VENV)/bin/streamlit

APP_KEY ?= default

# working directory is initialized from assistant Makefile
WORKING_DIR ?= ./

.PHONY: build start api clean db rag venv help bootstrap

.DEFAULT_GOAL := help

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

# venv and build both write into the shared $(VENV), so when two assistants'
# `make start` run at once they'd otherwise race two pip installs against the
# same site-packages (e.g. one deleting/rewriting the editable-install .pth
# file mid-write for the other). This mkdir-based lock is atomic and portable
# (no flock dependency on macOS), so the second invocation just waits.
VENV_LOCK := $(VENV)/.lock
define with_venv_lock
	@mkdir -p $(VENV); \
	while ! mkdir $(VENV_LOCK) 2>/dev/null; do sleep 0.5; done; \
	trap 'rmdir $(VENV_LOCK)' EXIT INT TERM; \
	$(1)
endef

venv: ## Create the virtualenv and install requirements
	$(call with_venv_lock,python3 -m venv $(VENV) && $(PIP) install -r requirements.txt)

build: ## Install this package into the virtualenv
	$(call with_venv_lock,$(PIP) install -e .)

db: ## Seed the database
	mkdir -p $(WORKING_DIR)/db
	WORKING_DIR=$(WORKING_DIR) $(PYTHON) $(WORKING_DIR)/resources/seed_data.py

api: ## Run the API server in the foreground
	WORKING_DIR=$(WORKING_DIR) $(PYTHON) $(WORKING_DIR)/api/main.py

rag: db ## Build the RAG index (implies db)
	WORKING_DIR=$(WORKING_DIR) $(PYTHON) $(WORKING_DIR)/resources/rag.py

# Each recipe line normally runs in its own shell, so the trailing "\"
# continuations below are needed to keep the backgrounded api process, the
# trap, and streamlit all in one shell — otherwise the trap can't see the
# api's PID and won't be able to clean it up.
start: build db rag ## Run the API in the background and Streamlit in the foreground
	WORKING_DIR=$(WORKING_DIR) $(PYTHON) $(WORKING_DIR)/api/main.py & \
	API_PID=$$!; \
	trap "kill $$API_PID 2>/dev/null" EXIT INT TERM; \
	$(STREAMLIT) run $(WORKING_DIR)/assistant.py

bootstrap: venv start ## Bootstrap

clean: ## Remove the virtualenv, build artifacts, and seeded db
	rm -rf $(VENV) chatbot_agents_examples.egg-info
	rm -rf $(WORKING_DIR)/db/
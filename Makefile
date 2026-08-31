VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
STREAMLIT := $(VENV)/bin/streamlit

APP_KEY ?= default

# working directory is initialized from assistant Makefile
WORKING_DIR ?= ./

.PHONY: build start api clean db rag venv

venv:
	python3 -m venv $(VENV)
	$(PIP) install -r requirements.txt

build:
	$(PIP) install -e .

db:
	mkdir -p $(WORKING_DIR)/db
	WORKING_DIR=$(WORKING_DIR) $(PYTHON) $(WORKING_DIR)/resources/seed_data.py

api:
	WORKING_DIR=$(WORKING_DIR) $(PYTHON) $(WORKING_DIR)/api/main.py

rag: db
	WORKING_DIR=$(WORKING_DIR) $(PYTHON) $(WORKING_DIR)/resources/rag.py

# Each recipe line normally runs in its own shell, so the trailing "\"
# continuations below are needed to keep the backgrounded api process, the
# trap, and streamlit all in one shell — otherwise the trap can't see the
# api's PID and won't be able to clean it up.
start: db rag
	WORKING_DIR=$(WORKING_DIR) $(PYTHON) $(WORKING_DIR)/api/main.py & \
	API_PID=$$!; \
	trap "kill $$API_PID 2>/dev/null" EXIT INT TERM; \
	$(STREAMLIT) run $(WORKING_DIR)/assistant.py

clean:
	rm -rf $(VENV) chatbot_agents_examples.egg-info
	rm -rf $(WORKING_DIR)/db/
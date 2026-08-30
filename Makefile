VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
STREAMLIT := $(VENV)/bin/streamlit

# Override on the command line, 
# e.g. `make start APP=banking_assistant`
# default: banking_assistant
APP ?= banking_assistant

.PHONY: build start clean db seed-db

build:
	python3 -m venv $(VENV)
	$(PIP) install -r requirements.txt
	$(PIP) install -e .

db:
	mkdir -p db/$(APP)
	$(PYTHON) assistants/$(APP)/resources/seed_data.py

start: build db
	$(STREAMLIT) run assistants/$(APP)/assistant.py

clean:
	rm -rf $(VENV) chatbot_agents_examples.egg-info
	rm -rf db/
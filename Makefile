VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
STREAMLIT := $(VENV)/bin/streamlit

# Override on the command line, 
# e.g. `make start APP=banking_assistant`
# default: banking_assistant
APP ?= banking_assistant

.PHONY: build start api clean db

build:
	python3 -m venv $(VENV)
	$(PIP) install -r requirements.txt
	$(PIP) install -e .

db:
	mkdir -p db/$(APP)
	$(PYTHON) assistants/$(APP)/resources/seed_data.py

api: build db
	$(PYTHON) assistants/$(APP)/api/main.py

# Each recipe line normally runs in its own shell, so the trailing "\"
# continuations below are needed to keep the backgrounded api process, the
# trap, and streamlit all in one shell — otherwise the trap can't see the
# api's PID and won't be able to clean it up.
start: build db
	$(PYTHON) assistants/$(APP)/api/main.py & \
	API_PID=$$!; \
	trap "kill $$API_PID 2>/dev/null" EXIT INT TERM; \
	$(STREAMLIT) run assistants/$(APP)/assistant.py

clean:
	rm -rf $(VENV) chatbot_agents_examples.egg-info
	rm -rf db/
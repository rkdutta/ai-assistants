VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
STREAMLIT := $(VENV)/bin/streamlit

.PHONY: build start clean db

build:
	python3 -m venv $(VENV)
	$(PIP) install -r requirements.txt
	$(PIP) install -e .

db:
	mkdir -p db

start: build db
	$(STREAMLIT) run assistants/banking.py

clean:
	rm -rf $(VENV) chatbot_agents_examples.egg-info

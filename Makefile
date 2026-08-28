VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
STREAMLIT := $(VENV)/bin/streamlit

.PHONY: build start clean

build:
	python3 -m venv $(VENV)
	$(PIP) install -r requirements.txt
	$(PIP) install -e .

start: build
	$(STREAMLIT) run assistants/banking.py

clean:
	rm -rf $(VENV) chatbot_agents_examples.egg-info

"""Streamlit entrypoint shared by every config-driven assistant.

Launched by `run.py start` via `streamlit run`. Reads WORKING_DIR from the
environment to find the assistant's assistant.yaml, builds the agent, and
renders the chat UI.
"""

import os

from library.chatbots import generic
from library.runtime.builder import ConfiguredAssistant
from library.runtime.config import AssistantConfig

cfg = AssistantConfig(os.environ["WORKING_DIR"])
generic.Chatbot(botname=cfg.name, agents=ConfiguredAssistant(cfg)).run()

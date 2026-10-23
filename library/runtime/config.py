"""Loads an assistant's declarative config (assistants/<name>/assistant.yaml).

Sections other than `name`/`key` are optional; an assistant only gets the
capability (model override, MCP, RAG, db seeding, API) it declares.

Also exports APP_KEY, APP_NAME, PORT and WORKING_DIR to the environment so
the scripts we spawn (seed_data.py, api/main.py, the MCP server) can read
them, and expands ${VAR} placeholders in the YAML values.
"""

import os
from pathlib import Path

import yaml
from dotenv import load_dotenv


class AssistantConfig:
    """Parsed assistant.yaml for one assistant, rooted at its working directory."""

    def __init__(self, working_dir: str):
        self.working_dir = working_dir
        self.dir = Path(working_dir)
        load_dotenv(self.dir / ".env")

        raw = yaml.safe_load((self.dir / "assistant.yaml").read_text(encoding="utf-8"))
        self.name = raw["name"]
        self.key = raw["key"]
        self.port = raw.get("port")

        # Scripts we spawn (seed_data.py, api/main.py, the MCP server) read
        # these from the environment, so export them before expanding ${...}.
        os.environ["WORKING_DIR"] = working_dir
        os.environ["APP_KEY"] = self.key
        os.environ["APP_NAME"] = self.name
        if self.port:
            os.environ["PORT"] = str(self.port)
        self.raw = self._expand(raw)

    @classmethod
    def _expand(cls, value):
        if isinstance(value, str):
            return os.path.expandvars(value)
        if isinstance(value, list):
            return [cls._expand(v) for v in value]
        if isinstance(value, dict):
            return {k: cls._expand(v) for k, v in value.items()}
        return value

    def section(self, name: str) -> dict | None:
        """The named YAML section, or None if the assistant doesn't declare it."""
        return self.raw.get(name) or None

    @property
    def system_prompt(self) -> str:
        return self.raw.get("system_prompt", "You are a helpful assistant.")

    @property
    def model(self) -> dict:
        return self.raw.get("model") or {}

    @property
    def mcp_servers(self) -> dict:
        return self.raw.get("mcp") or {}

    def path(self, relative: str) -> Path:
        """A path inside this assistant's directory."""
        return self.dir / relative

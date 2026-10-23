"""Builds a runnable agent from an AssistantConfig.

ConfiguredAssistant replaces the hand-written per-assistant Router classes:
the system prompt, model, MCP servers and RAG tool all come from the YAML.
"""

from library.agents.generic import Assistant
from library.runtime.config import AssistantConfig


class ConfiguredAssistant(Assistant):
    """An Assistant fully described by its AssistantConfig."""

    def __init__(self, cfg: AssistantConfig):
        self.cfg = cfg
        self.rag = None
        if cfg.section("rag"):
            from library.rags.generic import Rag
            self.rag = Rag(CHROMA_DIR=str(cfg.path("db")))
        super().__init__(
            mcpConfig=cfg.mcp_servers,
            llm_provider=cfg.model.get("provider"),
            model_name=cfg.model.get("name"),
        )

    def get_system_prompt(self) -> str:
        """System prompt from the YAML `system_prompt` key."""
        return self.cfg.system_prompt

    def get_tools(self) -> list:
        """Base tools plus the RAG search tool when `rag` is declared."""
        return super().get_tools() + (self.rag.get_tools() if self.rag else [])

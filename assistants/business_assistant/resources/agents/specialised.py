from library.agents.generic import Assistant
from resources.rag import rag

class Router(Assistant):

    def get_system_prompt(self) -> str:
        return "You are a business operations assistant."

    def get_tools(self) -> list:
        return super().get_tools() + rag.get_tools()

    def get_skills(self) -> list:
        extra_skill = []
        return super().get_skills() + extra_skill
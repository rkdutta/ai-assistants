from library.agents.generic import Assistant

class Router(Assistant):

    def get_system_prompt(self) -> str:
        return "You are a Banking operations assistant."

    def get_skills(self) -> list:
        extra_skill = []
        return super().get_skills() + extra_skill
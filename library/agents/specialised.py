import uuid
from library.agents.generic import Assistant

class BankingOpsAssistant(Assistant):

    def get_system_prompt(self) -> str:
        return "You are a Banking operations assistant."

    def get_skills(self) -> list:
        extra_skill = []
        return super().get_skills() + extra_skill


# testing code
if __name__ == '__main__':

    thread_id = uuid.uuid4()
    config = {"configurable":{ "thread_id": thread_id }}

    agent = BankingOpsAssistant(isLocal=True,inMemoryPersistance=True).get_bot()
    msg = agent.invoke({"messages": [{"role": "user", "content": "Hi"}]},config=config)
    print(msg["messages"][-1].content)
import os
from deepagents import create_deep_agent
from langchain_core.messages import BaseMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END, add_messages
from library.models.llm import llm as LLM
from langgraph.checkpoint.memory import InMemorySaver
from typing import Annotated, TypedDict
import uuid

class ChatbotState(TypedDict):
        messages: Annotated[list[BaseMessage], add_messages]

class Assistant:

    def __init__(self, isLocal: bool = True, inMemoryPersistance: bool = False):

        self.isLocal = isLocal
        self.inMemoryPersistance = inMemoryPersistance
        self.model = LLM(local = isLocal).get_llm()
        self.checkpointer = self.create_persistance()

        self.graph = StateGraph(ChatbotState)
        self.graph.add_node("chat_node", self.chat_node)
        self.graph.add_edge(START, "chat_node")
        self.graph.add_edge("chat_node", END)

        self.agent = create_deep_agent(
                model=self.model,
                tools=self.get_tools(),
                subagents=self.get_subagents(),
                checkpointer=self.checkpointer,
                system_prompt=self.get_system_prompt(),
                skills=self.get_skills()
            )

    def get_system_prompt(self) -> str:
        """Override in subclasses to define the assistant's system prompt."""
        raise NotImplementedError("Subclasses must implement get_system_prompt()")

    def get_tools(self) -> list:
        """Override in subclasses to give this assistant its own tools."""
        return []

    def get_subagents(self) -> list:
        """Override in subclasses to give this assistant its own subagents."""
        return []

    def get_skills(self) -> list:
        """Override in subclasses to give this assistant additional skills."""    
        return []  

    def chat_node(self,state: ChatbotState) -> ChatbotState:
        messages = state.get("messages")
        response = self.agent.invoke({"messages": messages})
        return {"messages": [response["messages"][-1]]}

    def get_bot(self):
         return self.graph.compile(checkpointer=self.checkpointer)

    def create_persistance(self):
         if self.inMemoryPersistance:
              return InMemorySaver()


# testing code
if __name__ == '__main__':

    thread_id = uuid.uuid4()
    config = {"configurable":{ "thread_id": thread_id }}

    agent = Assistant(isLocal=True,inMemoryPersistance=True).get_bot()
    msg = agent.invoke({"messages": [{"role": "user", "content": "Hi"}]},config=config)
    print(msg["messages"][-1].content)
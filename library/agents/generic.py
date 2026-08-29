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

    def __init__(self, isLocal: bool = True):
        self.model = LLM(local = isLocal).get_llm()
        self.checkpointer = InMemorySaver()

        self.graph = StateGraph(ChatbotState)
        self.graph.add_node("chat_node", self.chat_node)
        self.graph.add_edge(START, "chat_node")
        self.graph.add_edge("chat_node", END)

        self.agent = create_deep_agent(
                model=self.model,
                # tools=all_tools,
                # subagents=[billing_agent, customer_agent, supplier_agent],
                checkpointer=self.checkpointer,
                system_prompt=(
                    "You are a Banking operations assistant."
                ),
            )

    def chat_node(self,state: ChatbotState) -> ChatbotState:
        messages = state.get("messages")
        response = self.agent.invoke({"messages": messages})
        return {"messages": [response["messages"][-1]]}

    def getBot(self):
         return self.graph.compile(checkpointer=self.checkpointer)


# testing code
if __name__ == '__main__':

    thread_id = uuid.uuid4()
    config = {"configurable":{ "thread_id": thread_id }}

    agent = Assistant(isLocal=True).getBot()
    msg = agent.invoke({"messages": [{"role": "user", "content": "Hi"}]},config=config)
    print(msg["messages"][-1].content)
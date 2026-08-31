import asyncio
import os
from deepagents import create_deep_agent
from langchain_core.messages import BaseMessage
from langchain_core.tools import tool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import StateGraph, START, END, add_messages
from library.models.llm import llm as LLM
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
from typing import Annotated, TypedDict
import uuid
import sqlite3

class ChatbotState(TypedDict):
        messages: Annotated[list[BaseMessage], add_messages]

class Assistant:

    def __init__(self, botname: str = "chatbot", isLocal: bool = True, inMemoryPersistance: bool = False, mcpConfig: str = ""):

        self.botname = botname
        self.isLocal = isLocal
        self.inMemoryPersistance = inMemoryPersistance
        self.model = LLM(local = isLocal).get_llm()
        self.checkpointer = self.create_persistance()

        self.mcpConfig = mcpConfig

        self.graph = StateGraph(ChatbotState)
        self.graph.add_node("chat_node", self.chat_node)
        self.graph.add_edge(START, "chat_node")
        self.graph.add_edge("chat_node", END)

        self.agent = create_deep_agent(
                model=self.model,
                tools=self.get_tools() + self.get_mcp_tools(),
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

    def get_mcp_servers(self) -> dict:
        """Override in subclasses to configure the MCP servers this assistant
        should pull tools from. Keys are server names; values follow the
        langchain-mcp-adapters connection config (command/args/transport for
        stdio, or url/transport for streamable-http)."""
        if not self.mcpConfig:
            return {}
        # mcp.json follows the common "mcpServers" wrapper (Claude
        # Desktop/VS Code style); MultiServerMCPClient wants the flat
        # {server_name: config} dict underneath it.
        return self.mcpConfig.get("mcpServers", self.mcpConfig)

    def get_mcp_tools(self) -> list:
        servers = self.get_mcp_servers()
        print(">>>> MCP servers: ",servers)
        if not servers:
            return []
        client = MultiServerMCPClient(servers)
        print(">>>> MCP client: ",client)
        tools = asyncio.run(client.get_tools())
        print(">>>> MCP tools: ",tools)
        for t in tools:
            # MCP tools only ship a coroutine; the deep agent's tool node
            # invokes tools synchronously, so give each one a sync entrypoint
            # that runs its coroutine to completion.
            t.func = self._make_sync_tool_func(t.coroutine)
        return tools

    @staticmethod
    def _make_sync_tool_func(coroutine):
        def sync_func(*args, **kwargs):
            return asyncio.run(coroutine(*args, **kwargs))
        return sync_func

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
        db_name = self.botname.lower().replace(" ", "_")
        conn = sqlite3.connect(database=f"db/{db_name}/{db_name}.db",check_same_thread=False)
        return SqliteSaver(conn=conn)


# testing code
if __name__ == '__main__':

    thread_id = uuid.uuid4()
    config = {"configurable":{ "thread_id": thread_id }}

    agent = Assistant(botname="chatbot",isLocal=True,inMemoryPersistance=False).get_bot()
    msg = agent.invoke({"messages": [{"role": "user", "content": "Hi"}]},config=config)
    print(msg["messages"][-1].content)
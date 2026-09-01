import asyncio
from deepagents import create_deep_agent
from langchain_core.messages import BaseMessage
from langchain_core.tools import tool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import StateGraph, START, END, add_messages
from library.models.llm import llm as LLM
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
from typing import Annotated, TypedDict
import uuid, sqlite3, json, os

class ChatbotState(TypedDict):
        messages: Annotated[list[BaseMessage], add_messages]

class Assistant:

    def __init__(self, botname: str = "chatbot", isLocal: bool = True, inMemoryPersistance: bool = False, mcpConfig: json = {}):

        self.botname = botname
        self.isLocal = isLocal
        self.inMemoryPersistance = inMemoryPersistance
        self.model = LLM(local = isLocal).get_llm()
        self.checkpointer = self.create_persistance()

        self.mcpConfig = mcpConfig
        self.mcp_status = {}

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
        self.mcp_status = {}
        if not servers:
            return []
        tools = []
        for name, cfg in servers.items():
            try:
                client = MultiServerMCPClient({name: cfg})
                server_tools = asyncio.run(client.get_tools())
                for t in server_tools:
                    # MCP tools only ship a coroutine; the deep agent's tool node
                    # invokes tools synchronously, so give each one a sync entrypoint
                    # that runs its coroutine to completion.
                    t.func = self._make_sync_tool_func(t.coroutine)
                self.mcp_status[name] = {"connected": True, "tool_count": len(server_tools), "error": None}
                tools.extend(server_tools)
            except Exception as e:
                self.mcp_status[name] = {"connected": False, "tool_count": 0, "error": str(e)}
        print(">>>> MCP tools: ",tools)
        return tools

    def get_mcp_status(self) -> dict:
        """Per-server connection status, populated by the last get_mcp_tools() call."""
        return self.mcp_status

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
        WORKING_DIR = os.environ.get("WORKING_DIR")
        API_KEY = os.environ.get("API_KEY")
        conn = sqlite3.connect(database=f"{WORKING_DIR}/db/{API_KEY}.db", check_same_thread=False)
        return SqliteSaver(conn=conn)


# testing code
if __name__ == '__main__':

    thread_id = uuid.uuid4()
    config = {"configurable":{ "thread_id": thread_id }}

    agent = Assistant(botname="chatbot",isLocal=True,inMemoryPersistance=False).get_bot()
    msg = agent.invoke({"messages": [{"role": "user", "content": "Hi"}]},config=config)
    print(msg["messages"][-1].content)
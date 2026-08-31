from library.chatbots import generic
import json
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

APP_NAME = os.environ.get("APP_NAME", "Default Assistant")
APP_KEY = os.environ.get("APP_KEY", "default")

mcpConnection = f"assistants/{APP_KEY}/resources/mcp.json"
with open(mcpConnection, "r", encoding="utf-8") as f:
    mcpConfig = json.load(f)

bot = generic.Chatbot(
    botname=f"{APP_NAME}",
    keepChatHistoryFeature = True,
    generateNewChatFeature = True,
    inMemoryPersistance=False,
    mcpConfig = mcpConfig
)
bot.run()
from library.chatbots import generic
import json
import os
from pathlib import Path
from dotenv import load_dotenv

WORKING_DIR = os.environ.get("WORKING_DIR")
load_dotenv(f"{WORKING_DIR}/.env")

APP_KEY = os.environ.get("APP_KEY")
APP_NAME = os.environ.get("APP_NAME")
DB_PATH = Path(f"{WORKING_DIR}/db/{APP_KEY}.db")

mcpConnection = f"assistants/{APP_KEY}/resources/mcp.json"
with open(mcpConnection, "r", encoding="utf-8") as f:
    mcpConfig = json.load(f)
print(">>>>>> title = ",APP_NAME, APP_KEY)
bot = generic.Chatbot(
    botname=f"{APP_NAME}",
    keepChatHistoryFeature = True,
    generateNewChatFeature = True,
    inMemoryPersistance=False,
    mcpConfig = mcpConfig
)
bot.run()
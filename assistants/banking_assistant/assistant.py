import json,os
from library.chatbots import generic
from pathlib import Path
from dotenv import load_dotenv
from resources.agents.specialised import Router

WORKING_DIR = os.environ.get("WORKING_DIR")
load_dotenv(f"{WORKING_DIR}/.env")

APP_KEY = os.environ.get("APP_KEY")
APP_NAME = os.environ.get("APP_NAME")
DB_PATH = Path(f"{WORKING_DIR}/db/{APP_KEY}.db")

mcpConnection = f"{WORKING_DIR}/resources/mcp.json"
with open(mcpConnection, "r", encoding="utf-8") as f:
    # expand ${APP_KEY} etc. in the raw text; JSON itself has no substitution
    mcpConfig = json.loads(os.path.expandvars(f.read()))

bot = generic.Chatbot(
    botname=f"{APP_NAME}",
    agents =Router(
            mcpConfig=mcpConfig
        )
)
bot.run()
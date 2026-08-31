from library.chatbots import generic
import json

APP_NAME = "Banking Assistant"
APP_KEY = APP_NAME.lower().replace(" ", "_")

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
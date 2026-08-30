from library.chatbots import generic

bot = generic.Chatbot(
    botname="Banking Assistant",
    keepChatHistoryFeature = True,
    generateNewChatFeature = True,
    inMemoryPersistance=False
)
bot.run()
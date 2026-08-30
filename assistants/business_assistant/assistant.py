from library.chatbots import generic

bot = generic.Chatbot(
    botname="Business Assistant",
    keepChatHistoryFeature = True,
    generateNewChatFeature = True,
    inMemoryPersistance=False
)
bot.run()
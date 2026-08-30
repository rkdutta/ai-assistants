from library.chatbots import generic
import uuid


bot = generic.Chatbot(botname="Banking Assistant")
bot.configureFeatures(
     keepChatHistoryFeature = False,
     generateNewChatFeature = True
)
bot.run()
# import streamlit as st
# from langchain_core.messages import HumanMessage
from library.chatbots import chatbot
import uuid


bot = chatbot.Chatbot()
bot.configureFeatures(
     generateNewChat = True,
     keepHistory = False
)
bot.run()
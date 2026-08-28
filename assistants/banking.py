# import streamlit as st
# from langchain_core.messages import HumanMessage
from library.chatbots import generic
import uuid


bot = generic.Chatbot(botname="Banking Assistant")
bot.configureFeatures(
     generateNewChat = True,
     keepHistory = False
)
bot.run()
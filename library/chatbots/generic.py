from typing import Literal

import streamlit as st
import uuid

class Chatbot:

    def __init__(self, botname: str = ""):
        self.botname = botname or "My Chatbot Assistant"
        self.keepChatHistoryFeature = False
        self.generateNewChatFeature = False
        self.init()

    def loadChatHistory(self):
        for message in st.session_state["message_history"]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    def generateMessage(self, role: Literal["user", "assistant"], msg: str) -> str:
        return {"role": role, "content": msg}

    def recordChatHistory(self, role, msg):
        st.session_state["message_history"].append(self.generateMessage(role,msg))

    def generateNewChat(self):
        st.sidebar.button("New Chat")

    def initSession(self):

        if "message_history" not in st.session_state:
            st.session_state["message_history"] = []

        if "chat_threads" not in st.session_state:
                st.session_state["chat_threads"] = []

        if "thread_id" not in st.session_state:
                st.session_state.thread_id = uuid.uuid4()
        
    def init(self):
        with st.chat_message("assistant"):
            st.markdown(
                "Hello! I am your assistant. How can I help you today?"
            )
        st.sidebar.title(self.botname)
        self.initSession()

    def configureFeatures(self,keepChatHistoryFeature: bool = False, generateNewChatFeature: bool = False):

        self.keepChatHistoryFeature = keepChatHistoryFeature
        self.generateNewChatFeature = generateNewChatFeature

        if self.keepChatHistoryFeature:
            st.sidebar.header("History")
        if self.generateNewChatFeature:
            st.sidebar.button("New Chat")

    def generateAssistantResponse(self,msg: str):
         msg = "ai responded"
         return msg
         
    def run(self):
        self.loadChatHistory()
        user_input = st.chat_input("type here...")
        if user_input:
            role = "user"
            with st.chat_message(role):
                st.text(user_input)
                self.recordChatHistory(role,user_input)

            role = "assistant"
            with st.chat_message(role):
                assistant_response = self.generateAssistantResponse(user_input)
                st.markdown(assistant_response)
                self.recordChatHistory(role,assistant_response)
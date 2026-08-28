import streamlit as st
import uuid

class Chatbot:

    def __init__(self, botname: str = ""):
        self.botname = botname or "My Chatbot Assistant"
        self.init()
    
    def keepHistory(self):
        st.sidebar.header("History")

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

    def configureFeatures(self,keepHistory: bool = False, generateNewChat: bool = False):
        if keepHistory:
            self.keepHistory()
        if generateNewChat:
            self.generateNewChat()

    def run(self):
        user_input = st.chat_input("type here...")



# Quick tests
# bot = Chatbot()
# bot.configureFeatures(
#      generateNewChat = True,
#      keepHistory = False
# )
# bot.run()
from typing import Literal

import streamlit as st
import uuid

from library.agents.specialised import BankingOpsAssistant

class Chatbot:

    def __init__(self, botname: str = ""):
        self.botname = botname or "My Chatbot Assistant"
        self.keepChatHistoryFeature = False
        self.generateNewChatFeature = False
        self.agent = BankingOpsAssistant(isLocal=True,inMemoryPersistance=True).get_bot()
        self.init()

    def loadConversation(self):

        thread_id = st.session_state.thread_id

        print("loading conv. for thread_id=",thread_id)

        messages = st.session_state["live_chat"][thread_id]["message_history"]
        for message in messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    def switchThread(self, thread_id: uuid.UUID):
        st.session_state.thread_id = thread_id
        self.loadConversation()

    def log(self):
        print("\n\n----------\n\n")
        # print("Number of messages in history  = ", len(st.session_state["message_history"]))
        print("Number of chat threads in past = ", len(st.session_state["chat_threads"]))
        print("Current thread = ", st.session_state.thread_id)

        # print("Number of messages in history  = ", st.session_state["message_history"])
        # print("Number of chat threads in past = ", st.session_state["chat_threads"])

        # self.printCurrentState()
        # print("st.session_state  = ", st.session_state)

    def generateMessage(self, role: Literal["user", "assistant"], msg: str) -> str:
        return {"role": role, "content": msg}

    def recordChatHistory(self, role, msg):
        st.session_state["live_chat"][st.session_state.thread_id]["message_history"].append(self.generateMessage(role,msg))

    def generateNewChat(self):
        st.session_state.thread_id = uuid.uuid4()
        st.session_state["live_chat"][st.session_state.thread_id] = {}
        st.session_state["live_chat"][st.session_state.thread_id]["message_history"] = []
        self.addThread(st.session_state.thread_id)
        self.loadConversation()

    def addThread(self,thread_id: uuid.UUID):
        if thread_id not in st.session_state.chat_threads:
            st.session_state.chat_threads.append(thread_id)
        
    def initSession(self):

        if "chat_threads" not in st.session_state:
                st.session_state["chat_threads"] = []

        if "thread_id" not in st.session_state:
                st.session_state.thread_id = uuid.uuid4()
                self.addThread(st.session_state.thread_id)

        if "live_chat" not in st.session_state:
            st.session_state["live_chat"] = {}
            if st.session_state.thread_id not in st.session_state["live_chat"]:
                st.session_state["live_chat"][st.session_state.thread_id] = {}
                if "message_history" not in st.session_state["live_chat"][st.session_state.thread_id]:
                    st.session_state["live_chat"][st.session_state.thread_id]["message_history"] = []

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

        if self.generateNewChatFeature:
            st.sidebar.button("New Chat",on_click=self.generateNewChat)

        if self.keepChatHistoryFeature:
            st.sidebar.header("History")
            self.loadChatThreads()

        self.loadConversation()
            
    def generateChatTitle(self,tid: uuid.UUID):
        title = str(tid)
        return title
    
    def loadChatThreads(self):
            for tid in st.session_state.chat_threads:
                label = self.generateChatTitle(tid)
                st.sidebar.button(label, on_click=self.switchThread, args=(tid,))

    def generateAssistantResponse(self,msg: str):
        config = {"configurable":{ "thread_id": st.session_state.thread_id }}
        msg = self.agent.invoke({"messages": [{"role": "user", "content": msg}]},config=config)
        return msg["messages"][-1].content

    def getThreadConfig(self):
        config = {"configurable": {"thread_id": st.session_state.thread_id}}     
        return config

    def printCurrentState(self):
        state = self.agent.get_state(config=self.getThreadConfig())
        print(state)
        
    def run(self):

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

        self.log()
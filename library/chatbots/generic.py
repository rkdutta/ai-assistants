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

    def loadConversation(self, thread_id: uuid.UUID = None):
        if thread_id is None:
            thread_id = st.session_state.thread_id
        
        # messages = self.agent.get_state(config={"configurable": {"thread_id": thread_id}})
        # for message in st.session_state["message_history"]:
        #     with st.chat_message(message["role"]):
        #         st.markdown(message["content"])
        # print(messages)
        # for message in messages:
        #             with st.chat_message(message["role"]):
        #                 st.markdown(message["content"])


    def log(self):
        print("\n\n----------\n\n")
        print("Number of messages in history  = ", len(st.session_state["message_history"]))
        print("Number of chat threads in past = ", len(st.session_state["chat_threads"]))
        print("Current thread = ", st.session_state.thread_id)

        # print("Number of messages in history  = ", st.session_state["message_history"])
        print("Number of chat threads in past = ", st.session_state["chat_threads"])

    def generateMessage(self, role: Literal["user", "assistant"], msg: str) -> str:
        return {"role": role, "content": msg}

    def recordChatHistory(self, role, msg):
        st.session_state["message_history"].append(self.generateMessage(role,msg))

    def generateNewChat(self):
        st.session_state.thread_id = uuid.uuid4()
        st.session_state["message_history"] = []
        self.addThread(st.session_state.thread_id)

    def addThread(self,thread_id: uuid.UUID):
        if thread_id not in st.session_state.chat_threads:
            st.session_state.chat_threads.append(thread_id)
        
    def initSession(self):

        if "message_history" not in st.session_state:
            st.session_state["message_history"] = []

        if "chat_threads" not in st.session_state:
                st.session_state["chat_threads"] = []

        if "thread_id" not in st.session_state:
                st.session_state.thread_id = uuid.uuid4()
                self.addThread(st.session_state.thread_id)
        
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

    def generateChatTitle(self,tid: uuid.UUID):
        title = str(tid)
        return title
    
    def loadChatThreads(self):
        if self.keepChatHistoryFeature:
            for tid in st.session_state.chat_threads:
                label = self.generateChatTitle(tid)
                st.sidebar.button(label, on_click=self.loadConversation(tid))

    def generateAssistantResponse(self,msg: str):
        config = {"configurable":{ "thread_id": st.session_state.thread_id }}
        msg = self.agent.invoke({"messages": [{"role": "user", "content": msg}]},config=config)
        return msg["messages"][-1].content

    def getThreadConfig(self):
        config = {"configurable": {"thread_id": st.session_state.thread_id}}     
        return config

    def run(self):
        # self.loadConversation()
        # self.loadChatThreads()
        user_input = st.chat_input("type here...")
        # if user_input:
        #     role = "user"
        #     with st.chat_message(role):
        #         st.text(user_input)
        #         self.recordChatHistory(role,user_input)

        #     role = "assistant"
        #     with st.chat_message(role):
        #         assistant_response = self.generateAssistantResponse(user_input)
        #         st.markdown(assistant_response)
        #         self.recordChatHistory(role,assistant_response)

        self.log()
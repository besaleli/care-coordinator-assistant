"""Main app module"""
import os
from typing import List, Self
import requests
from pydantic import BaseModel, model_validator
import streamlit as st
from care_ml.utils import fake_stream
from care_ml.ml.message import Message, Role

ML_URL = os.getenv('ML_URL')

class ChatHistory(BaseModel):
    """Chat history handler."""
    @model_validator(mode='after')
    def _init_chat_history(self) -> Self:
        if "messages" not in st.session_state:
            st.session_state.messages = []

        if any(i["role"] == Role.SYSTEM for i in st.session_state.messages):
            raise ValueError("Customer-facing chat history must not contain a system message")

        return self

    @property
    def messages(self) -> List[Message]:
        return [Message(**i) for i in st.session_state.messages]

    def append(self, m: Message) -> None:
        if m.role == Role.SYSTEM:
            raise ValueError("Customer-facing chat history must not contain a system message")

        st.session_state.messages.append(m.model_dump())

    def call_ml_services(self, messages: List[Message]) -> Message:
        url = f"{ML_URL}/message/create"
        print(url)
        ml_response = requests.post(
            url,
            json={
                "messages": [i.model_dump() for i in messages]
            },
            timeout=30
            )

        return Message(**ml_response.json()["message"])

    def step(self, prompt: str):
        st.chat_message(Role.USER).markdown(prompt)

        self.append(Message(role=Role.USER, content=prompt))
        response = self.call_ml_services(self.messages)

        with st.chat_message(response.role):
            st.write_stream(fake_stream(response.content))

        self.append(response)

st.title("Care Coordinator Assistant 🧑‍⚕️")

# Initialize chat history
chat_history = ChatHistory()

for message in chat_history.messages:
    with st.chat_message(message.role):
        st.markdown(message.content)

# React to user input
if user_prompt := st.chat_input("What's up 🫡"):
    chat_history.step(user_prompt)

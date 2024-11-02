"""Main app module"""
import os
from typing import List, Self
import time
import requests
from pydantic import BaseModel, model_validator, field_validator
import streamlit as st
from care_ml.ml.message import Message, Role

ML_URL = os.getenv('ML_URL')

class CustomerFacingMessage(Message):
    """Customer-facing message."""
    @field_validator('role')
    @classmethod
    def validate_role(cls, v):
        """Make sure customer-facing chat history does not contain a system message."""
        if v == Role.SYSTEM:
            raise ValueError("Customer-facing chat history must not contain a system message")

        return v

class ChatHistory(BaseModel):
    """Chat history handler."""
    @model_validator(mode='after')
    def _init_chat_history(self) -> Self:
        if "messages" not in st.session_state:
            st.session_state.messages = []

        return self

    @property
    def messages(self) -> List[Message]:
        """Accessor for chat history stored in streamlit state dictionary."""
        return [CustomerFacingMessage(**i) for i in st.session_state.messages]

    def _append(self, m: Message) -> None:
        if m.role == Role.SYSTEM:
            raise ValueError("Customer-facing chat history must not contain a system message")

        st.session_state.messages.append(m.model_dump())

    def _call_ml_services(self, messages: List[Message]) -> Message:
        url = f"{ML_URL}/message/create"
        print(url)
        ml_response = requests.post(
            url,
            json={
                "messages": [i.model_dump() for i in messages]
            },
            timeout=30
            )

        return CustomerFacingMessage(**ml_response.json()["message"])

    def step(self, prompt: str):
        """Complete a dialogue step with the given chat history."""
        st.chat_message(Role.USER).markdown(prompt)

        self._append(Message(role=Role.USER, content=prompt))
        response = self._call_ml_services(self.messages)
        with st.spinner("typing..."):
            time.sleep(1)
            with st.chat_message(response.role):
                st.markdown(response.content)

        self._append(response)

st.title("Care Coordinator Assistant 🧑‍⚕️")

# Initialize chat history
chat_history = ChatHistory()

for message in chat_history.messages:
    with st.chat_message(message.role):
        st.markdown(message.content)

# React to user input
if user_prompt := st.chat_input("What's up 🫡"):
    chat_history.step(user_prompt)

"""Main app module"""
import streamlit as st
from care_app.utils import fake_stream

st.title("Care Coordinator Assistant 🧑‍⚕️")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What's up 🫡"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    response = f"Echo: {prompt}"
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.write_stream(fake_stream(response))
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

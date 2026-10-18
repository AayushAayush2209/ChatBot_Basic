import streamlit as st
from backend import chatbot
from langchain_core.messages import HumanMessage

CONFIG = {"configurable": {"thread_id": "thread-1"}}

if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

# Display previous messages
for message in st.session_state["message_history"]:
    with st.chat_message(message["role"]):
        st.write(message["content"])

user_input = st.chat_input("Type here")

if user_input:
    st.session_state["message_history"].append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.write(user_input)

    assistant_response = []

    def stream_response():
        for message_chunk, _ in chatbot.stream(
            {"messages": [HumanMessage(content=user_input)]},
            config=CONFIG,
            stream_mode="messages",
        ):
            if message_chunk.content:
                assistant_response.append(message_chunk.content)
                yield message_chunk.content

    with st.chat_message("assistant"):
        st.write_stream(stream_response)

    st.session_state["message_history"].append(
        {"role": "assistant", "content": "".join(assistant_response)}
    )
import streamlit as st
from backend import chatbot
from langchain_core.messages import HumanMessage
import uuid


#Utility Function

def generate_thread_id():
    thread_id=uuid.uuid4()
    return thread_id

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(st.session_state["thread_id"])
    st.session_state['message_history'] = []

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id) 

CONFIG = {"configurable": {"thread_id": st.session_state["thread_id"]}}

if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

if "thread_id" not in st.session_state:
    st.session_state["thread_id"]=generate_thread_id()


if "chat_thread" not in st.session_state:
    st.session_state["chat_thread"] = []
add_thread(st.session_state["thread_id"])


#sidebar UI
st.sidebar("LangGraph ChatBot")
if st.button("New Chat"):
    reset_chat()
st.header("New Conversation")

for thread_id in st.session_state["chat_thread"]:
    st.sidebar.button(str(thread_id))

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
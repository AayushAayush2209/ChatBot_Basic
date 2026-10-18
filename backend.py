from __future__ import annotations

import os
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, BaseMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

load_dotenv()


def _build_model():
    """Create the Ollama chat model used by the app."""
    try:
        from langchain_ollama import ChatOllama
    except ImportError:
        return None

    model_name = os.getenv("OLLAMA_MODEL", "llama3.2")
    try:
        return ChatOllama(model=model_name, temperature=0.7)
    except Exception:
        return None


model = _build_model()


class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def chat_node(state: ChatState):
    messages = state["messages"]

    if model is None:
        latest_message = messages[-1].content if messages else ""
        response = AIMessage(
            content=(
                "Ollama is not configured or not running. Start Ollama and pull a model such as llama3.2, then set OLLAMA_MODEL. "
                f"Last user message: {latest_message}"
            )
        )
        return {"messages": [response]}

    try:
        response = model.invoke(messages)
    except Exception as exc:
        latest_message = messages[-1].content if messages else ""
        response = AIMessage(
            content=(
                "Ollama connection failed. Make sure the Ollama server is running and the model is installed. "
                f"Last user message: {latest_message}. Error: {exc}"
            )
        )
    return {"messages": [response]}


checkpointer = InMemorySaver()

graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)
chatbot = graph.compile(checkpointer=checkpointer)



import asyncio
import logging

import streamlit as st

from src.agents.llm_agent import ask_pharmaflow
from src.agents.error_handler import handle_ai_error


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


# Streamlit page configuration
st.set_page_config(
    page_title="PharmaFlow AI Assistant",
    page_icon="💊",
    layout="wide",
)


# Dashboard heading
st.title("💊 PharmaFlow AI Analytics Assistant")

st.caption(
    "Local AI powered by Qwen3, Ollama and MCP"
)

st.info(
    "Ask questions about pharmacy branches, "
    "medicine revenue and supplier spending."
)


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []


# Sidebar controls
with st.sidebar:
    st.header("PharmaFlow AI")

    st.write("**AI Model:** Qwen3 4B")
    st.write("**AI Runtime:** Ollama")
    st.write("**Integration:** MCP")
    st.write("**Access:** Read-only analytics")

    if st.button("Clear chat history"):
        st.session_state.messages = []
        st.rerun()


# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Chat input
question = st.chat_input(
    "Ask PharmaFlow about pharmacy analytics..."
)


# Process user question
if question:

    # Store the user's message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    # Display user message
    with st.chat_message("user"):
        st.markdown(question)

    # Generate AI response
    with st.chat_message("assistant"):

        with st.spinner("Analyzing pharmacy data..."):

            try:
                logger.info(
                    "Processing PharmaFlow AI request"
                )

                answer = asyncio.run(
                    ask_pharmaflow(question)
                )

                logger.info(
                    "PharmaFlow AI request completed"
                )

            except Exception as error:
                answer = handle_ai_error(error)

        # Display response
        st.markdown(answer)

    # Save assistant response
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )

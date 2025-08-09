import streamlit as st
import requests
import json
import uuid
import os
from datetime import datetime
from typing import Optional, Dict, Any
import time

# Configuration
API_BASE_URL = os.environ.get("API_BASE_URL", "http://backend:8000")  # Docker service name or localhost


class ChatClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def send_message(self, message: str, session_id: Optional[str] = None, use_rag: bool = True) -> Dict[str, Any]:
        """Send a message to the chat API"""
        try:
            response = requests.post(
                f"{self.base_url}/chat",
                json={
                    "message": message,
                    "session_id": session_id,
                    "use_rag": use_rag
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Error connecting to API: {e}")
            return None

    def get_session_history(self, session_id: str) -> Dict[str, Any]:
        """Get session history"""
        try:
            response = requests.get(f"{self.base_url}/sessions/{session_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching session: {e}")
            return None

    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        try:
            response = requests.delete(f"{self.base_url}/sessions/{session_id}")
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            st.error(f"Error deleting session: {e}")
            return False

    def get_health_status(self) -> Dict[str, Any]:
        """Get API health status"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"status": "unhealthy", "error": str(e)}


def initialize_session_state():
    """Initialize Streamlit session state"""
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "chat_client" not in st.session_state:
        st.session_state.chat_client = ChatClient(API_BASE_URL)


def display_chat_messages():
    """Display chat messages"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

            # Show metadata for assistant messages
            if message["role"] == "assistant" and "metadata" in message:
                with st.expander("Message Details", expanded=False):
                    meta = message["metadata"]
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Used RAG:** {meta.get('used_rag', 'Unknown')}")
                        st.write(f"**Message Count:** {meta.get('message_count', 'Unknown')}")
                    with col2:
                        if meta.get('context_used'):
                            st.write("**Context Used:**")
                            st.code(meta['context_used'], language=None)


def display_sidebar():
    """Display sidebar with controls"""
    with st.sidebar:
        st.header("🤖 Chat Controls")

        # RAG Toggle
        use_rag = st.toggle("Enable RAG", value=True, help="Use Retrieval-Augmented Generation for enhanced responses")

        st.divider()

        # Session Info
        st.subheader("📊 Session Info")
        st.write(f"**Session ID:** `{st.session_state.session_id[:8]}...`")
        st.write(f"**Messages:** {len(st.session_state.messages)}")

        # Session Actions
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                if st.session_state.chat_client.delete_session(st.session_state.session_id):
                    st.session_state.messages = []
                    st.session_state.session_id = str(uuid.uuid4())
                    st.rerun()

        with col2:
            if st.button("🔄 New Session", use_container_width=True):
                st.session_state.messages = []
                st.session_state.session_id = str(uuid.uuid4())
                st.rerun()

        st.divider()

        # API Health Status
        st.subheader("🏥 API Status")
        health_status = st.session_state.chat_client.get_health_status()

        if health_status.get("status") == "healthy":
            st.success("✅ API Online")

            # Show detailed status if available
            if "rag_service" in health_status:
                rag_info = health_status["rag_service"]
                st.write(f"**RAG Enabled:** {'✅' if rag_info.get('rag_enabled') else '❌'}")
                st.write(f"**Model Ready:** {'✅' if rag_info.get('model_initialized') else '❌'}")

            if "sessions" in health_status:
                sessions_info = health_status["sessions"]
                st.write(f"**Active Sessions:** {sessions_info.get('active_count', 0)}")
        else:
            st.error("❌ API Offline")
            if "error" in health_status:
                st.write(f"Error: {health_status['error']}")

        # Refresh button
        if st.button("🔄 Refresh Status", use_container_width=True):
            st.rerun()

        st.divider()

        # Settings
        st.subheader("⚙️ Settings")
        api_url = st.text_input("API URL", value=API_BASE_URL, help="FastAPI server URL")
        if api_url != API_BASE_URL:
            st.session_state.chat_client = ChatClient(api_url)

        return use_rag


def main():
    """Main Streamlit application"""
    st.set_page_config(
        page_title="RAG Chat Interface",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Initialize session state
    initialize_session_state()

    # Main header
    st.title("🤖 RAG Chat Interface")
    st.caption("Chat with AI using Retrieval-Augmented Generation or regular conversation mode")

    # Display sidebar and get RAG preference
    use_rag = display_sidebar()

    # Chat mode indicator
    if use_rag:
        st.info("🔍 **RAG Mode Active** - Responses will use knowledge base context")
    else:
        st.info("💬 **Chat Mode Active** - Regular conversation without knowledge base")

    # Display existing messages
    display_chat_messages()

    # Chat input
    if prompt := st.chat_input("What would you like to know?"):
        # Add user message to chat
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "timestamp": datetime.now().isoformat()
        })

        # Display user message immediately
        with st.chat_message("user"):
            st.write(prompt)

        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response_data = st.session_state.chat_client.send_message(
                    message=prompt,
                    session_id=st.session_state.session_id,
                    use_rag=use_rag
                )

            if response_data:
                # Display response
                st.write(response_data["response"])

                # Store assistant message with metadata
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_data["response"],
                    "timestamp": datetime.now().isoformat(),
                    "metadata": {
                        "used_rag": response_data.get("used_rag", False),
                        "message_count": response_data.get("message_count", 0),
                        "context_used": response_data.get("context_used"),
                        "session_id": response_data.get("session_id")
                    }
                })

                # Update session ID if it changed
                if response_data.get("session_id") != st.session_state.session_id:
                    st.session_state.session_id = response_data["session_id"]

                # Show response metadata
                with st.expander("Response Details", expanded=False):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Used RAG:** {response_data.get('used_rag', 'Unknown')}")
                        st.write(f"**Message Count:** {response_data.get('message_count', 0)}")
                    with col2:
                        if response_data.get('context_used'):
                            st.write("**RAG Context Used:**")
                            st.code(response_data['context_used'], language=None)
            else:
                st.error("Failed to get response from the API. Please check the connection.")

    # Footer
    st.divider()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.caption("💡 Toggle RAG mode in the sidebar to switch between knowledge-enhanced and regular responses")


if __name__ == "__main__":
    main()
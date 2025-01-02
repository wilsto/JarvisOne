"""Sidebar component for conversation history."""

import streamlit as st
from datetime import datetime, timezone
import logging
from typing import Optional, Callable, List, Dict
from ..styles.sidebar import SIDEBAR_STYLE

logger = logging.getLogger(__name__)

def format_timestamp(dt: datetime) -> str:
    """Format timestamp in a user-friendly way."""
    now = datetime.now(timezone.utc)
    # Ensure dt is timezone-aware
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    diff = now - dt
    
    if diff.days == 0:
        return dt.strftime("%H:%M")
    elif diff.days < 7:
        return dt.strftime("%A")
    else:
        return dt.strftime("%d/%m/%y")

# Style CSS pour les cartes
CARD_STYLE = """
    .conversation-card {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 8px;
        transition: background-color 0.2s ease;
        display: flex;
        flex-direction: column;
        position: relative;
        gap: 4px;
    }
    .conversation-card:hover {
        background-color: #f5f5f5;
    }
    .conversation-card-title {
        font-size: 1.1em;
        font-weight: bold;
        color: #2c3e50;
        flex: 1;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .conversation-card-time {
        font-size: 0.8em;
        color: #777;
        white-space: nowrap;
        margin-left: 8px;
    }
    .conversation-card-details {
        display: flex;
        align-items: center;
        width: 100%;
    }
    .conversation-card-last-message {
        font-size: 0.9em;
        color: #666;
        line-height: 1.4;
        overflow: hidden;
        text-overflow: ellipsis;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        word-break: break-word;
    }
    /* Style for the button */
    .stButton button {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        opacity: 0;
        cursor: pointer;
        margin: 0;
        padding: 0;
    }
"""
def render_conversation_history(
    conversations: List[Dict],
    on_conversation_selected: Callable[[str], None],
    current_conversation_id: Optional[str] = None
):
    """Render the conversation history in the sidebar."""
    # Inject custom CSS with style tags
    st.markdown(f"<style>{CARD_STYLE}</style>", unsafe_allow_html=True)
    
    # Initialize search state if not exists
    if 'search_query' not in st.session_state:
        st.session_state.search_query = ""
    
    # Search box
    search_query = st.text_input(
        "Search conversations...",
        value=st.session_state.search_query,
        key="history_search",
        label_visibility="collapsed",
        placeholder="Search conversations..."
    )
    
    # Update search state
    st.session_state.search_query = search_query
    
    # Filter conversations based on search
    filtered_conversations = []
    for conv in conversations:
        title = conv.get("title", "").lower()
        messages = conv.get("messages", [])
        content = " ".join([msg.get("content", "") for msg in messages]).lower()
        if search_query.lower() in title or search_query.lower() in content:
            filtered_conversations.append(conv)
    
    # Display conversations
    for conversation in filtered_conversations:
        render_conversation_item(conversation, on_conversation_selected, current_conversation_id)

def render_conversation_item(
    conversation: Dict,
    on_conversation_selected: Callable,
    current_conversation_id: Optional[str]
):
    """Render a single conversation item."""
    is_active = conversation["id"] == current_conversation_id
    title = conversation["title"] or "New Chat"
    timestamp = format_timestamp(conversation["last_timestamp"])
    
    # Safely get and truncate the last message
    try:
        last_message = conversation.get("messages", [])[-1].get("content", "No message")
        # Truncate long messages
        if len(last_message) > 100:
            last_message = last_message[:100] + "..."
        # Escape HTML characters to prevent formatting issues
        last_message = last_message.replace("<", "&lt;").replace(">", "&gt;")
    except (IndexError, KeyError):
        last_message = "No message"
    
    # Create container for better layout
    container = st.container()
    with container:
        # Render the conversation card
        st.markdown(f"""
            <div class="conversation-card" style='{"background-color: #e8f0fe;" if is_active else ""}'>
                <div class="conversation-card-details">
                    <span class="conversation-card-title">{title}</span>
                    <span class="conversation-card-time">{timestamp}</span>
                </div>
                <div class="conversation-card-last-message" title="{last_message}">
                    {last_message}
                </div>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        # Add an invisible button that covers the entire container
        if st.button("", key=f"conv_{conversation['id']}", help=title):
            on_conversation_selected(conversation["id"])
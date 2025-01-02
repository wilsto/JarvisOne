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
    .conversation-card-details {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
    }
    .conversation-card-time-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 4px;
    }
    .conversation-card-time {
        color: #666;
        font-size: 0.9em;
    }
    .conversation-card-last-message {
        color: #666;
        font-size: 0.9em;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .stButton button {
        border: none;
        background-color: transparent;
    }
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
    
    # Check if this conversation is being loading
    is_loading = st.session_state.get('loading_conversation', False) and conversation["id"] == current_conversation_id
    
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
        # Add loading spinner if conversation is being loaded
        if is_loading:
            st.spinner("Loading conversation...")
        
        # Create columns for layout
        title_col, time_col = st.columns([4, 1])
        
        with title_col:
            st.markdown(f"""
                <div style='background-color: {"#e8f0fe" if is_active else ""}; opacity: {"0.7" if is_loading else "1"}; padding: 8px; border-radius: 8px;'>
                    <div style='font-weight: bold; font-size: 1.1em; color: #2c3e50;'>{title}</div>
                    <div style='color: #666; font-size: 0.9em; margin-top: 4px;'>{last_message}</div>
                </div>
                """, 
                unsafe_allow_html=True
            )
        
        with time_col:
            st.markdown(f"""
                <div style='text-align: center;'>
                    <div style='color: #666; font-size: 0.9em;'>{timestamp}
                """,
                unsafe_allow_html=True
            )
            if not is_loading:
                st.button("🔄", key=f"reload_{conversation['id']}", help="Reload conversation", on_click=lambda: on_conversation_selected(conversation["id"]))

            st.markdown(f"""
               </div> </div>
                """,
                unsafe_allow_html=True
            )                
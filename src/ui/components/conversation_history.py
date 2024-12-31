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

def render_conversation_history(
    conversations: List[Dict],
    on_conversation_selected: Callable[[str], None],
    current_conversation_id: Optional[str] = None
):
    """Render the conversation history in the sidebar."""
    # Inject custom CSS
    st.markdown(SIDEBAR_STYLE, unsafe_allow_html=True)
    
    # Initialize search state if not exists
    if 'search_query' not in st.session_state:
        st.session_state.search_query = ''
    
    # Search bar
    search_col1, search_col2 = st.columns([1, 7])
    with search_col1:
        st.markdown(
            '<div style="padding-top: 20px;padding-left: 10px">🔎</div>',
            unsafe_allow_html=True
        )
    with search_col2:
        search_query = st.text_input(
            "Search conversations",
            value=st.session_state.search_query,
            label_visibility="collapsed",
            placeholder="Search conversations..."
        )

    
    # Update search state
    st.session_state.search_query = search_query
    
    # Filter conversations based on search query
    if search_query:
        filtered_conversations = []
        search_term = search_query.lower()
        
        for conv in conversations:
            # Search in title
            title = conv.get("title") or ""
            if search_term in title.lower():
                filtered_conversations.append(conv)
                continue
            
            # Search in messages
            messages = conv.get("messages", [])
            for msg in messages:
                content = msg.get("content") or ""
                if search_term in content.lower():
                    filtered_conversations.append(conv)
                    break
    else:
        filtered_conversations = conversations
        
    # Display filtered conversations
    if filtered_conversations:
        for conv in filtered_conversations:
            render_conversation_item(conv, on_conversation_selected, current_conversation_id)
    else:
        if search_query:
            st.markdown('<div style="padding: 8px 0; color: #666; font-size: 13px;">No matching conversations</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="padding: 8px 0; color: #666; font-size: 13px;">No conversations yet</div>', unsafe_allow_html=True)

def render_conversation_item(
    conversation: Dict,
    on_conversation_selected: Callable,
    current_conversation_id: Optional[str]
):
    """Render a single conversation item."""
    is_active = conversation["id"] == current_conversation_id
    title = conversation["title"] or "New Chat"
    timestamp = format_timestamp(conversation["last_timestamp"])
    
    # Create container for better layout
    container = st.container()
    with container:
        col1, col2, col3 = st.columns([1, 6, 1])
        with col1:
            st.markdown(
                f'<div style="text-align: right; padding: 0.75rem 0.5rem;color: #666; font-size: 10px;margin-top: 10px">{timestamp}</div>',
                unsafe_allow_html=True
            )        
        with col2:
            st.markdown(
                f'<div style="text-align: left; padding: 0.75rem 0.5rem;margin-top: 6px">{title}</div>',
                unsafe_allow_html=True
            )
            
        with col3:
            if st.button(
                "⤴",
                key=f"conv_{conversation['id']}",
                use_container_width=True,
                type="secondary" if is_active else "primary"
            ):
                on_conversation_selected(conversation["id"])

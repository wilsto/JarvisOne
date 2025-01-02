"""Sidebar component for conversation history."""

import streamlit as st
from datetime import datetime, timezone, timedelta
import logging
from typing import Optional, Callable, List, Dict
from ..styles.sidebar import SIDEBAR_STYLE

logger = logging.getLogger(__name__)

def format_timestamp(dt: datetime) -> str:
    """Format timestamp in a user-friendly way.
    
    Returns:
        - "HH:MM" for today
        - "Yesterday HH:MM" for yesterday
        - "Monday HH:MM" (etc.) for this week
        - "Jan 15 HH:MM" for this month
        - "Jan 15, 2024" for older dates
    """
    now = datetime.now(timezone.utc)
    
    # Ensure dt is timezone-aware
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    # Convert to start of day for accurate comparison
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    dt_start = dt.replace(hour=0, minute=0, second=0, microsecond=0)
    
    diff_days = (today_start - dt_start).days
    time_str = dt.strftime("%H:%M")
    
    if diff_days == 0:
        return time_str
    elif diff_days == 1:
        return f"{time_str}"
    elif diff_days < 7:
        return f"{dt.strftime('%A')} {time_str}"  # Day name
    elif diff_days < 30:
        return f"{dt.strftime('%b %d')} {time_str}"  # Month day
    else:
        return dt.strftime("%b %d, %Y")  # Full date

def group_conversations_by_time(conversations: List[Dict]) -> Dict[str, List[Dict]]:
    """Group conversations by time period."""
    now = datetime.now(timezone.utc)
    
    # Convert now to start of day for accurate day comparisons
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_start = today_start - timedelta(days=1)
    week_start = today_start - timedelta(days=7)
    month_start = today_start - timedelta(days=30)
    
    groups = {
        "Today": [],
        "Yesterday": [],
        "This Week": [],
        "This Month": [],
        "Older": []
    }
    
    for conv in conversations:
        # Ensure timestamp is UTC
        dt = conv["last_timestamp"]
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        
        # Convert to start of day for accurate comparison
        dt_start = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        
        if dt_start >= today_start:
            groups["Today"].append(conv)
        elif dt_start >= yesterday_start:
            groups["Yesterday"].append(conv)
        elif dt_start >= week_start:
            groups["This Week"].append(conv)
        elif dt_start >= month_start:
            groups["This Month"].append(conv)
        else:
            groups["Older"].append(conv)
    
    # Only return non-empty groups
    return {k: sorted(v, key=lambda x: x["last_timestamp"], reverse=True) 
            for k, v in groups.items() if v}

# Style CSS pour les cartes et séparateurs
CARD_STYLE = """

    .time-separator {
        color: #666;
        font-size: 0.85em;
        font-weight: 500;
        padding: 8px 0;
        margin: 8px 0;
        border-bottom: 1px solid #eee;
    }
    .stButton button {
        border: none;
        background-color: transparent;
        color: #666;
        font-size: 0.7em;
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
    
    # Search box with improved styling
    search_query = st.text_input(
        "Search conversations...",
        value=st.session_state.search_query,
        key="history_search",
        label_visibility="collapsed",
        placeholder="🔍 Search conversations..."
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
    
    # Group conversations by time period
    grouped_conversations = group_conversations_by_time(filtered_conversations)
    
    # Display conversations by group
    for group_name, group_conversations in grouped_conversations.items():
        # Add time separator
        st.markdown(f'<div class="time-separator">{group_name}</div>', unsafe_allow_html=True)
        
        # Sort conversations within group by timestamp (newest first)
        sorted_conversations = sorted(
            group_conversations,
            key=lambda x: x["last_timestamp"],
            reverse=True
        )
        
        # Display conversations in the group
        for conversation in sorted_conversations:
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
        time_col, title_col  = st.columns([0.75, 9])
        
        with title_col:
            st.markdown(f"""
                <div style='background-color: {"#e8f0fe" if is_active else ""}; opacity: {"0.7" if is_loading else "1"}; padding: 8px; border-radius: 8px;'>
                    <div style='font-weight: bold; font-size: 1em; color: #2c3e50;'>{title}</div>
                    <div style='color: #666; font-size: 0.8em; margin-top: 0px;'>{last_message}</div>
                </div>
                """, 
                unsafe_allow_html=True
            )
        
        with time_col:
            st.markdown(f"""
                <div style='text-align: center;'>
                    <div style='color: #666; font-size: 0.8em;'>{timestamp}
                """,
                unsafe_allow_html=True
            )
            if not is_loading:
                st.button(" 🔄", key=f"reload_{conversation['id']}", help="Reload conversation", on_click=lambda: on_conversation_selected(conversation["id"]))

            st.markdown(f"""
               </div> </div>
                """,
                unsafe_allow_html=True
            )                
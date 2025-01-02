"""Chat UI module for JarvisOne."""

import streamlit as st
from features.chat_processor import ChatProcessor
from .components.sidebar import render_sidebar
import uuid
from datetime import datetime
from core.prompts.generic_prompts import generate_welcome_message

__all__ = ['display_chat', 'init_chat_session']

def init_chat_processor():
    """Initialize or get the chat processor from session state."""
    if "chat_processor" not in st.session_state:
        st.session_state.chat_processor = ChatProcessor()
    return st.session_state.chat_processor

def init_chat_session():
    """Initialize the chat session with welcome message if not already initialized."""
    # Ensure chat processor is initialized first
    chat_processor = init_chat_processor()
    
    messages = chat_processor.get_messages()
    if not messages:  # Only add welcome message if no messages exist
        # Get current workspace scope from workspace manager
        workspace_manager = st.session_state.get('workspace_manager')
        
        if workspace_manager:
            current_space_config = workspace_manager.get_current_space_config()
            
            if current_space_config and hasattr(current_space_config, 'metadata'):
                scope = current_space_config.metadata.get('scope', '')
                welcome_message = generate_welcome_message(scope)
            else:
                # Fallback welcome message if no scope defined
                welcome_message = (
                    "👋 Bonjour, je suis JarvisOne, votre assistant IA !\n\n"
                    "Comment puis-je vous aider aujourd'hui ?"
                )
        else:
            # Fallback welcome message if no workspace manager
            welcome_message = (
                "👋 Bonjour, je suis JarvisOne, votre assistant IA !\n\n"
                "Comment puis-je vous aider aujourd'hui ?"
            )
        
        chat_processor.add_message("assistant", welcome_message)

def render_chat_header(chat_processor):
    """Render the chat header with actions."""
    col1, col2, col3, col4 = st.columns([7,1,1,1])
    
    with col1:
        if st.session_state.current_conversation_id:
            conversation = chat_processor.repository.get_conversation(st.session_state.current_conversation_id)
            if conversation and conversation.get('title'):
                st.markdown(f"<div style='display: flex; align-items: center; margin-top: 20px; margin-left: 10px;'><span style='margin-right: 8px; font-size: 1.2em; font-weight: bold;'> 🗨️ {conversation['title']}</span></div>", unsafe_allow_html=True)
            else:
                st.markdown("<div style='display: flex; align-items: center;  margin-top: 20px; margin-left: 10px;'><span style='margin-right: 8px; font-size: 1.2em; font-weight: bold;'>🗨️ New Chat</span></div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='display: flex; align-items: center;  margin-top: 20px; margin-left: 10px;'><span style='margin-right: 8px; font-size: 1.2em; font-weight: bold;'>🗨️ New Chat</span></div>", unsafe_allow_html=True)
            
    with col2:
        # Tools label
        st.markdown("<div style='text-align: right; padding-right: 5px; color: #666; font-size: 12px; margin-top: 22px; margin-bottom: 20px;'>Tools</div>", unsafe_allow_html=True)

    with col3:
        if st.button("🆕", use_container_width=True):
            # Create new conversation using ChatProcessor
            chat_processor.new_conversation()
            st.rerun()
            
    with col4:
        if st.button("🗑️", use_container_width=True):
            if st.session_state.current_conversation_id:
                chat_processor.repository.delete_conversation(st.session_state.current_conversation_id)
                st.session_state.current_conversation_id = None
                st.rerun()

   
def display_chat():
    """Display the chat interface."""
    # Initialize chat processor
    chat_processor = init_chat_processor()
    
    # Initialize chat session
    init_chat_session()
    
    # Render the chat header
    render_chat_header(chat_processor)
    
    # Render the sidebar
    render_sidebar()

    # Display chat messages
    for message in chat_processor.get_messages():
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("Parlez à JarvisOne"):
        # Add and display user message
        chat_processor.add_message("user", prompt)
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get and display bot response
        with st.chat_message("assistant"):
            response = chat_processor.process_user_input(prompt)
            st.markdown(response)
            chat_processor.add_message("assistant", response)
    
    # Check if we need to rerun the app (e.g., after loading a conversation)
    if st.session_state.get('should_rerun', False):
        st.session_state.should_rerun = False  # Reset the flag
        st.rerun()
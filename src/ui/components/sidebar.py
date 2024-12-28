import streamlit as st
import logging
from datetime import datetime
from pathlib import Path
import yaml
from core.workspace_manager import SpaceType
from .conversation_history import render_conversation_history

logger = logging.getLogger(__name__)

def render_sidebar():
    """Render the sidebar with workspace configuration options."""
    with st.sidebar:
        # Add title to sidebar header
        st.header("🤖 JarvisOne",
                          anchor="cool-header",
                  help="This is a custom header",
                  divider="rainbow")
        
        # Workspace Selection
        space_options = [
            ("General", SpaceType.AGNOSTIC),
            ("Work", SpaceType.WORK),
            ("Personal", SpaceType.PERSONAL),
            ("Dev", SpaceType.DEV),
            ("Coaching", SpaceType.COACHING),
        ]
        
        current_index = next(
            (i for i, (_, space_type) in enumerate(space_options) 
             if space_type == st.session_state.workspace), 
            0
        )
        
        selected_space = st.selectbox(
            "Workspace",
            options=[name for name, _ in space_options],
            index=current_index,
            key="workspace_select"
        )
        
        # Update Workspace if changed
        selected_space_type = next(space_type for name, space_type in space_options if name == selected_space)
        if selected_space_type != st.session_state.workspace:
            old_space = st.session_state.workspace
            st.session_state.workspace = selected_space_type
            
            # Update workspace manager
            st.session_state.workspace_manager.set_current_space(selected_space_type)
            
            # Create new conversation in new workspace if chat processor exists
            if "chat_processor" in st.session_state:
                st.session_state.chat_processor.new_conversation(workspace=selected_space_type)
            
            # Update app state
            config_file = Path(__file__).parent.parent.parent.parent / "config" / "app_state.yaml"
            current_state = {}
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    current_state = yaml.safe_load(f)
            
            current_state["workspace"] = selected_space_type.name
            
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(current_state, f)
            
            logger.info(f"Switched Workspace from {old_space} to {selected_space_type}")
            
            # Rerun to update UI
            st.rerun()

        # Render conversation history if chat processor is available
        if "chat_processor" in st.session_state:
            chat_processor = st.session_state.chat_processor
            current_space = st.session_state.workspace
            conversations = chat_processor.get_recent_conversations(workspace=current_space)
            
            def on_conversation_selected(conversation_id):
                if conversation_id is None:
                    # Create new conversation in current workspace
                    chat_processor.new_conversation(workspace=current_space)
                else:
                    chat_processor.load_conversation(conversation_id)
                st.rerun()
            
            render_conversation_history(
                conversations=conversations,
                on_conversation_selected=on_conversation_selected,
                current_conversation_id=st.session_state.get("current_conversation_id")
            )

import streamlit as st
import logging
from datetime import datetime
from pathlib import Path
import yaml
from core.workspace_manager import SpaceType
from core.config_manager import ConfigManager
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
        
        #TODO: add https://github.com/victoryhb/streamlit-option-menu
        selected_space = st.selectbox(
            "Workspace",
            options=range(len(space_options)),
            format_func=lambda x: space_options[x][0],
            index=current_index,
            key="workspace_selector"
        )
        
        # Update workspace if changed
        if space_options[selected_space][1] != st.session_state.workspace:
            old_space = st.session_state.workspace
            workspace_manager = st.session_state.workspace_manager
            new_space = space_options[selected_space][1]
            
            # Update workspace manager and session state
            workspace_manager.set_current_space(new_space)
            st.session_state.workspace = new_space
            
            # Save workspace preference (this will also update app_state)
            ConfigManager.save_workspace_preferences(new_space.name)
            
            # Reset role when workspace changes
            st.session_state.current_role = None
            
            # Create new conversation in new workspace if chat processor exists
            if "chat_processor" in st.session_state:
                st.session_state.chat_processor.new_conversation(workspace=new_space)
            
            # Log workspace change
            logger.info(f"Switched Workspace from {old_space} to {new_space}")
            
            # Only rerun if workspace actually changed
            if old_space != new_space:
                st.rerun()
        
        # Role Selection (if workspace has roles)
        workspace_manager = st.session_state.workspace_manager
        roles = workspace_manager.get_current_space_roles()
        
        if roles:
            # Initialize current_role in session_state if not present
            if 'current_role' not in st.session_state:
                st.session_state.current_role = roles[0]['name'] if roles else None
                if st.session_state.current_role:
                    workspace_manager.set_current_role(st.session_state.current_role)
            
            role_options = [(role['name'], role['description']) for role in roles]
            current_role_index = next(
                (i for i, (name, _) in enumerate(role_options) 
                 if name == st.session_state.current_role),
                0
            )
            
            selected_role = st.selectbox(
                "Role",
                options=range(len(role_options)),
                format_func=lambda x: role_options[x][1],
                index=current_role_index,
                key="role_selector"
            )
            
            # Update role if changed
            new_role = role_options[selected_role][0]
            if new_role != st.session_state.current_role:
                old_role = st.session_state.current_role
                workspace_manager.set_current_role(new_role)
                st.session_state.current_role = new_role
                
                # Save workspace preferences with new role
                ConfigManager.save_workspace_preferences(
                    st.session_state.workspace.name,
                    new_role
                )
                
                # Log role change
                logger.info(f"Changed role from {old_role} to {new_role} in workspace {st.session_state.workspace.name}")
                
                # Create new conversation for new role
                if "chat_processor" in st.session_state:
                    st.session_state.chat_processor.new_conversation(workspace=st.session_state.workspace)
                
                # Rerun to update UI with new role context
                st.rerun()

        # Add a separator before the LLM control sliders
        st.divider()
                
        # Initialize default values in session state if not present
        if "llm_creativity" not in st.session_state:
            st.session_state.llm_creativity = 1  # Default to balanced
        if "llm_style" not in st.session_state:
            st.session_state.llm_style = 1      # Default to Casual
        if "llm_length" not in st.session_state:
            st.session_state.llm_length = 1     # Default to balanced
                
        # Creativity slider
        st.session_state.llm_creativity = st.select_slider(
            "🎨 Creativity Level",
            options=[0, 1, 2],
            value=st.session_state.llm_creativity,
            format_func=lambda x: ["Strict", "Balanced", "Creative"][x],
            key="creativity_slider"
        )

        # Style slider
        st.session_state.llm_style = st.select_slider(
            "🎭 Response Style",
            options=[0, 1, 2],
            value=st.session_state.llm_style,
            format_func=lambda x: ["Professional", "Casual", "Fun"][x],
            key="style_slider"
        )

        # Length slider
        st.session_state.llm_length = st.select_slider(
            "📏 Response Length",
            options=[0, 1, 2],
            value=st.session_state.llm_length,
            format_func=lambda x: ["Short", "Balanced", "Long"][x],
            key="length_slider"
        )

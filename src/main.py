import streamlit as st
from utils.logging_config import setup_logging, get_logs
from ui.chat_ui import display_chat, init_chat_session
from ui.interactions import InteractionDisplayFactory
from ui.styles import get_all_styles
from core.workspace_manager import WorkspaceManager, SpaceType
from pathlib import Path
from core.core_agent import CoreAgent
from core.database.db_cleaner import clean_database
from core.database.models import init_database
from sqlalchemy.orm import sessionmaker
from ui.apps import display_apps
import yaml
from datetime import datetime
from core.config_manager import ConfigManager  # Import ConfigManager

# Configure logging first
setup_logging()

def load_app_state() -> dict:
    """Load application state from configuration file."""
    config = ConfigManager._load_config()
    return config.get("app_state", {
        "workspace": "AGNOSTIC",
        "cache_enabled": True
    })

def initialize_session_state():
    """Initialize session state with default values if not already set."""
    # Load app state
    app_state = load_app_state()
    
    # Initialize workspace first
    if 'workspace' not in st.session_state:
        st.session_state.workspace = SpaceType[app_state["workspace"]]
        print(f"Initialized workspace to: {st.session_state.workspace}")  # Debug
    
    if 'workspace_manager' not in st.session_state:
        config_dir = Path(__file__).parent.parent / "config"
        st.session_state.workspace_manager = WorkspaceManager(config_dir)
        st.session_state.workspace_manager.set_current_space(st.session_state.workspace)
        print("Created new workspace manager")  # Debug
        print(f"Set current space to: {st.session_state.workspace}")  # Debug
    else:
        # Sync current space with workspace manager
        st.session_state.workspace_manager.set_current_space(st.session_state.workspace)
        print(f"Synchronized workspace manager to: {st.session_state.workspace}")  # Debug

    # Initialize cache state
    if 'cache_enabled' not in st.session_state:
        st.session_state.cache_enabled = app_state.get('cache_enabled', True)

def get_search_title(query: str) -> str:
    """Generate a short and explicit title for the search."""
    # Extract keywords from the query
    words = query.lower().split()
    if "ext:" in query:
        # If the search contains an extension
        for word in words:
            if word.startswith("ext:"):
                return f"Files {word[4:].upper()}"
    elif any(word.startswith("dm:") for word in words):
        # If the search contains a date
        return "Recent files"
    else:
        # Otherwise, take the first 3 significant words
        significant_words = [w for w in words if len(w) > 2 and not w.startswith(("le", "la", "les", "un", "une", "des"))]
        return " ".join(significant_words[:3]).title()

def display_logs():
    """Display logs in a dedicated tab."""
    # Search bar and filter button on the same line
    search_col, button_col = st.columns([5,1])
    
    with search_col:
        search_term = st.text_input("🔍 Search logs", "")
    
    with button_col:
        show_filters = st.button("⚙️", key="show_filters", use_container_width=True)
    
    # Filtering options in an expander
    if show_filters:
        with st.expander("Filters", expanded=True):
            level_filter = st.multiselect(
                "Log level",
                ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                default=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            )
    else:
        level_filter = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    
    # Retrieve and filter logs
    logs = get_logs()
    if level_filter:
        logs = [log for log in logs if log['level'] in level_filter]
    if search_term:
        logs = [log for log in logs if search_term.lower() in log['message'].lower()]
    
    # Display logs
    for log in reversed(logs):  # From most recent to oldest
        color = {
            'DEBUG': '#6c757d',
            'INFO': '#0d6efd',
            'WARNING': '#ffc107',
            'ERROR': '#dc3545',
            'CRITICAL': '#dc3545'
        }.get(log['level'], 'black')
        
        st.markdown(
            f'<div class="log-entry">'
            f'<span style="color:{color}">[{log["timestamp"]}] [{log["level"]}]</span> '
            f'{log["message"]}'
            f'</div>',
            unsafe_allow_html=True
        )

def display_interactions():
    """Display interactions and search results."""
    if "interactions" not in st.session_state:
        st.session_state.interactions = []
        
    if not st.session_state.interactions:
        st.info("No interactions yet. Search results will appear here.")
        return
    
    # Reverse the order of interactions to have the most recent at the top
    interactions = list(reversed(st.session_state.interactions))
    
    # Display each interaction
    for i, interaction in enumerate(interactions):
        # Retrieve the appropriate handler
        handler = InteractionDisplayFactory.get_display_handler(interaction['type'])
        
        # Create an expander with the title generated by the handler
        with st.expander(handler.get_expander_title(interaction), expanded=(i == 0)):
            handler.display(interaction)

def create_agent(agent_type: str) -> CoreAgent:
    """Create and initialize an agent with the current workspace."""
    agent = CoreAgent(
        agent_name=agent_type,
        system_instructions=f"You are a {agent_type} agent.",  # Simple instructions for now
        workspace_manager=st.session_state.workspace_manager
    )
    return agent

def save_app_state(space_type: SpaceType):
    """Save the application state."""
    config = ConfigManager._load_config()
    config["app_state"] = {
        "workspace": space_type.name,
        "cache_enabled": st.session_state.cache_enabled
    }
    ConfigManager.save_config(config)

def sidebar():
    """Render the sidebar."""
    with st.sidebar:
        st.title("JarvisOne")
        
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
        
        # Cache Control
        cache_enabled = st.toggle(
            "Enable cache",
            value=st.session_state.cache_enabled,
            help="Enable or disable cache",
            key="cache_toggle"
        )
        
        # Update cache state if changed
        if cache_enabled != st.session_state.cache_enabled:
            old_value = st.session_state.cache_enabled
            st.session_state.cache_enabled = cache_enabled
            current_state = load_app_state()
            current_state["cache_enabled"] = cache_enabled
            config_file = Path(__file__).parent.parent / "config" / "app_state.yaml"
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(current_state, f)
            
            # Log the configuration change
            if 'interactions' not in st.session_state:
                st.session_state.interactions = []
            st.session_state.interactions.append({
                'type': 'config_change',
                'config_type': 'Cache',
                'old_value': str(old_value),
                'new_value': str(cache_enabled),
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            st.rerun()
        
        # Update Workspace if changed
        selected_space_type = next(space_type for name, space_type in space_options if name == selected_space)
        if selected_space_type != st.session_state.workspace:
            old_space = st.session_state.workspace
            
            # First save the state to ensure persistence
            save_app_state(selected_space_type)
            
            # Then update workspace manager
            st.session_state.workspace_manager.set_current_space(selected_space_type)
            
            # Update session state after workspace manager
            st.session_state.workspace = selected_space_type
            
            # Clear chat state to force reinitialization
            if 'chat_processor' in st.session_state:
                del st.session_state.chat_processor
            if 'messages' in st.session_state:
                del st.session_state.messages
            
            # Log the configuration change
            if 'interactions' not in st.session_state:
                st.session_state.interactions = []
            st.session_state.interactions.append({
                'type': 'config_change',
                'config_type': 'Workspace',
                'old_value': old_space.name,
                'new_value': selected_space_type.name,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            
            # Force a complete rerun to reinitialize everything
            st.rerun()

# Configure style to use full width
config = ConfigManager._load_config()
ui_config = config.get("ui", {})
theme = ui_config.get("theme", "default")

st.set_page_config( 
    page_title="JarvisOne",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/yourusername/JarvisOne',
        'Report a bug': "https://github.com/yourusername/JarvisOne/issues",
        'About': "# JarvisOne\nA modular, scalable, conversational AI assistant."
    }
)

# Load and apply CSS styles
st.markdown(f"<style>{get_all_styles()}</style>", unsafe_allow_html=True)

# Initialize session state first
initialize_session_state()

# Initialize chat session after workspace initialization
init_chat_session()

if __name__ == "__main__":
    # Create two main columns with ratio 2:1
    col_main, col_side = st.columns([3, 2])
    
    # Main column for chat (2/3)
    with col_main:
        chat_tab, library_tab, apps_tab = st.tabs(["💬 Chat", "📚 Library", "🔧 Apps"])
        with chat_tab:
            st.markdown('<div id="chat-tab-content">', unsafe_allow_html=True)
            display_chat()  # Your function that generates chat content
            st.markdown('</div>', unsafe_allow_html=True)
        with library_tab:
            st.markdown("### Library")
            st.info("Library features coming soon!")
        with apps_tab:
            display_apps()

    # Side column for logs and interactions (1/3)
    with col_side:
        tab_interactions, tab_logs, tab_params = st.tabs([
            "⚡ Interactions", 
            "📋 Logs",
            "⚙️ Parameters"
        ])
        
        with tab_interactions:
            display_interactions()
        
        with tab_logs:
            display_logs()
            
        with tab_params:
            from ui.parameters import display_parameters
            display_parameters()
            
    # Count errors in the background
    logs = get_logs()
    error_count = sum(1 for log in logs if log['level'] in ['ERROR', 'CRITICAL'])
    if error_count > 0:
        st.sidebar.error(f"{error_count} error(s) detected. Check logs for more details.")
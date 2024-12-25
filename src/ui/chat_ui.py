import streamlit as st
from features.chat_processor import ChatProcessor
from .components.sidebar import render_sidebar

def init_chat_processor():
    """Initialize or get the chat processor from session state."""
    if "chat_processor" not in st.session_state:
        st.session_state.chat_processor = ChatProcessor()
    return st.session_state.chat_processor

def init_chat_session():
    """Initialize the chat session with welcome message if not already initialized."""
    welcome_message = (
        "👋 Bonjour, je suis JarvisOne, votre assistant IA !\n\n"
        "Je peux vous aider avec :\n"
        "• La recherche de fichiers et de code\n"
        "• L'analyse de code et le débogage\n"
        "• La création et modification de fichiers\n"
        "• L'exécution de commandes\n\n"
        "Comment puis-je vous aider aujourd'hui ?"
    )
    
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": welcome_message}]

def handle_suggestion_click(suggestion: str):
    """Handle click on suggestion button."""
    st.session_state.messages.append({"role": "user", "content": suggestion})
    chat_processor = st.session_state.chat_processor
    response = chat_processor.process_user_input(suggestion)
    st.session_state.messages.append({"role": "assistant", "content": response})
    # Force refresh
    st.rerun()

def display_suggestions(suggestions: list):
    """Display suggestion buttons in columns."""
    if suggestions:
        st.write("💡 Suggestions:")
        # Créer des colonnes pour les boutons (3 par ligne)
        cols = st.columns(min(3, len(suggestions)))
        for idx, suggestion in enumerate(suggestions):
            col_idx = idx % 3
            with cols[col_idx]:
                st.button(
                    suggestion,
                    key=f"suggestion_{idx}",
                    on_click=handle_suggestion_click,
                    args=(suggestion,),
                    use_container_width=True
                )

def display_suggestions_new(suggestions: list):
    """Display clickable suggestion buttons."""
    for suggestion in suggestions:
        if st.button(suggestion, key=f"suggestion_{suggestion}"):
            st.session_state.messages.append({"role": "user", "content": suggestion})
            st.rerun()

def display_chat():
    # Initialize chat processor
    chat_processor = init_chat_processor()
    
    # Initialize chat session
    init_chat_session()
    
    # Render the sidebar
    render_sidebar()
    
    # Add CSS to position chat at bottom
    st.markdown("""
        <style>
        [data-testid="stChatInput"] {
            position: fixed;
            bottom: 0;
            background: white;
            max-width: calc(100% - 300px); /* Adjust for sidebar */
            padding: 1rem;
            z-index: 1000;
        }
        .stChatMessage {
            margin-bottom: 1rem;
        }
        </style>
    """, unsafe_allow_html=True)

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            # Si c'est un message de l'assistant, extraire les suggestions
            if message["role"] == "assistant" and "💡 Suggestions :" in message["content"]:
                suggestions = [
                    line.replace("• ", "").strip()
                    for line in message["content"].split("\n")
                    if line.startswith("• ")
                ]
                # Afficher les suggestions comme boutons
                display_suggestions_new(suggestions)

    # Accept user input
    if prompt := st.chat_input("Parlez à JarvisOne"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get bot response
        with st.chat_message("assistant"):
            response = chat_processor.process_user_input(prompt)
            st.markdown(response)
            
            # Extraire et afficher les suggestions comme boutons
            if "💡 Suggestions :" in response:
                suggestions = [
                    line.replace("• ", "").strip()
                    for line in response.split("\n")
                    if line.startswith("• ")
                ]
                display_suggestions_new(suggestions)
            
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
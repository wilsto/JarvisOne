"""Apps UI module for JarvisOne."""

import streamlit as st
from core.database.models import init_database
from core.database.db_cleaner import clean_database, reset_database
from sqlalchemy.orm import sessionmaker
from pathlib import Path

def display_db_cleaning():
    """Display database cleaning interface and functionality."""

    # Database Tools Section
    st.markdown("### 🛠️ Database Tools")
    
    # Clean Database Section
    with st.expander("🧹 Database Cleaning", expanded=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("Clean up orphaned records and fix inconsistencies in the database.")
        with col2:
             if st.button("Clean Database", type="primary", help="Start database cleaning process", key="clean_db_button"):
                # Initialize database connection
                db_path = Path(__file__).parent.parent.parent / "data" / "conversations.db"
                engine = init_database(str(db_path))
                Session = sessionmaker(bind=engine)
                session = Session()
                
                try:
                    with st.spinner("Cleaning database..."):
                        stats = clean_database(session)
                    
                    # Display results in a nice format
                    st.success("Database cleaning completed successfully!")
                    
                    # Create two columns for stats
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("##### Removed Items")
                        st.markdown(f"- 🗑️ Messages without conversation: **{stats['null_conversation_messages_removed']}**")
                        st.markdown(f"- 🗑️ Orphaned messages: **{stats['orphaned_messages_removed']}**")
                        st.markdown(f"- 🗑️ Empty conversations: **{stats['empty_conversations_removed']}**")
                    
                    with col2:
                        st.markdown("##### Other Operations")
                        st.markdown(f"- 📝 Untitled conversations: **{stats['untitled_conversations_removed']}**")
                        st.markdown(f"- 🏷️ Orphaned topics: **{stats['orphaned_topics_removed']}**")
                        st.markdown(f"- 🔄 Duplicate topics: **{stats['duplicate_topics_removed']}**")
                        st.markdown(f"- 🔧 Invalid workspaces fixed: **{stats['invalid_workspace_fixed']}**")
                    
                    # Display total items affected
                    total_items = sum(stats.values())
                    st.markdown(f"#### Total Items Affected: **{total_items}**")
                    
                except Exception as e:
                    st.error(f"Error during database cleaning: {str(e)}")
                finally:
                    session.close()
            
    # Danger Zone
    st.markdown("### ⚠️ Danger Zone")
    
    # Reset Database Section
    with st.expander("Reset Database", expanded=True):
         col1, col2 = st.columns([3, 1])
         with col1:
            st.markdown('<p style="color: #24292f; font-size: 0.9rem; margin-bottom: 1rem;">⚠️ This will permanently delete all conversations and messages. This action cannot be undone.</p>', unsafe_allow_html=True)
         with col2:
            # Two-step confirmation using session state
            if 'confirm_reset' not in st.session_state:
                st.session_state.confirm_reset = False
            if not st.session_state.confirm_reset:
                st.button("Reset Database", key="reset_btn", help="Click to initiate database reset", type="primary")
            else:
                # Show warning message
                st.warning("⚠️ **WARNING**: You are about to permanently delete all conversations and messages. This action cannot be undone.", icon="⚠️")
                
                # Container for confirmation buttons
                if st.button("Confirm",  key="confirm_reset_btn", help="Click to confirm reset", type="primary"):
                    # Initialize database connection
                    db_path = Path(__file__).parent.parent.parent / "data" / "conversations.db"
                    engine = init_database(str(db_path))
                    Session = sessionmaker(bind=engine)
                    session = Session()
                    
                    try:
                        with st.spinner("Resetting database..."):
                            stats = reset_database(session)
                        
                        # Display results
                        st.success("Database has been reset!")
                        st.markdown(f"- 🗑️ Conversations removed: **{stats['conversations_removed']}**")
                        st.markdown(f"- 🗑️ Messages removed: **{stats['messages_removed']}**")
                        st.markdown(f"- 🗑️ Topics removed: **{stats['topics_removed']}**")
                        
                    except Exception as e:
                        st.error(f"Error during database reset: {str(e)}")
                    finally:
                        session.close()
                        st.session_state.confirm_reset = False
                if st.button("Cancel", key="cancel_reset_btn"):
                    st.session_state.confirm_reset = False
                    st.rerun()

def display_apps():
    """Display the apps interface with all available tools."""
    # Database Tools Section
    st.markdown("### 🛠️ Application Tools")
    display_db_cleaning()
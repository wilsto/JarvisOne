"""Apps UI module for JarvisOne."""

import streamlit as st
from core.database.models import init_database
from core.database.db_cleaner import clean_database
from sqlalchemy.orm import sessionmaker
from pathlib import Path

def display_db_cleaning():
    """Display database cleaning interface and functionality."""
    st.markdown("### 🧹 Database Cleaning")
    
    if st.button("Clean Database", type="primary"):
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
            
            # Display stats in columns
            with col1:
                st.markdown("#### Removed Items")
                st.markdown(f"- 🗑️ Messages without conversation: **{stats['null_conversation_messages_removed']}**")
                st.markdown(f"- 🗑️ Orphaned messages: **{stats['orphaned_messages_removed']}**")
                st.markdown(f"- 🗑️ Empty conversations: **{stats['empty_conversations_removed']}**")
            
            with col2:
                st.markdown("#### Other Operations")
                st.markdown(f"- 📝 Untitled conversations: **{stats['untitled_conversations_removed']}**")
                st.markdown(f"- 🏷️ Orphaned topics: **{stats['orphaned_topics_removed']}**")
                st.markdown(f"- 🔄 Duplicate topics: **{stats['duplicate_topics_removed']}**")
            
            # Display total items affected
            total_items = sum(stats.values())
            st.markdown(f"#### Total Items Affected: **{total_items}**")
            
        except Exception as e:
            st.error(f"Error during database cleaning: {str(e)}")
        finally:
            session.close()

def display_apps():
    """Display the apps interface with all available tools."""
    # Database Tools Section
    st.markdown("## 🛠️ Database Tools")
    display_db_cleaning()

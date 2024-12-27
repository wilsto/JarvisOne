"""Styles for the sidebar components."""

SIDEBAR_STYLE = """
<style>
    /* Global Sidebar Styles */
    [data-testid="stSidebar"] {
        background-color: #FAFAFA;
    }
    
    /* Search Bar */
    [data-testid="stTextInput"] {
        padding: 0 !important;
    }
    [data-testid="stTextInput"] > div {
        padding: 0 !important;
    }
    [data-testid="stTextInput"] input {
        padding: 8px 12px !important;
        border: 1px solid #E8E8E8 !important;
        border-radius: 8px !important;
        font-size: 14px !important;
    }
    .search-shortcut {
        color: #666;
        background: #F0F0F0;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 12px;
        float: right;
    }
    
    /* Navigation */
    .nav-item {
        display: flex;
        align-items: center;
        padding: 8px 12px;
        color: #1a1a1a;
        text-decoration: none;
        font-size: 14px;
        margin: 2px 8px;
        border-radius: 6px;
        transition: background 0.2s;
    }
    .nav-item:hover {
        background: #F0F0F0;
    }
    .nav-item.active {
        background: #E8E8E8;
    }
    .nav-icon {
        margin-right: 12px;
        color: #666;
    }
    .nav-shortcut {
        margin-left: auto;
        color: #666;
        font-size: 12px;
    }
    
    /* Section Headers */
    .section-header {
        color: #666;
        font-size: 12px;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        padding: 16px 20px 8px;
        margin: 0;
    }
    
    /* Conversation Items */
    .conversation-item {
        padding: 8px 12px;
        margin: 2px 8px;
        border-radius: 6px;
        cursor: pointer;
        transition: background 0.2s;
        font-size: 14px;
    }
    .conversation-item:hover {
        background: #F0F0F0;
    }
    .conversation-item.active {
        background: #E8E8E8;
    }
    [data-testid="stButton"] {
        text-align: left !important;
    }
    [data-testid="stButton"] button {
        width: 100%;
        text-align: left !important;
        padding: 8px 0;
    }
    .conversation-meta {
        font-size: 12px;
        color: #666;
        margin-top: -12px;
        padding-left: 8px;
    }
    
    /* Override Streamlit button styles */
    .stButton button {
        width: 100%;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: #1a1a1a !important;
        font-size: 14px !important;
        padding: 8px 12px !important;
        margin: 2px 0 !important;
        text-align: left !important;
    }
    .stButton button:hover {
        background: #F0F0F0 !important;
        color: #1a1a1a !important;
    }
    .stButton button[kind="secondary"] {
        background: #E8E8E8 !important;
    }
    
    /* Tool Buttons */
    [data-testid="stButton"] button {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0.25rem !important;
        min-height: 0 !important;
    }
    [data-testid="stButton"] button:hover {
        background: #F0F0F0 !important;
        border-radius: 4px;
    }
    [data-testid="stButton"] button div {
        font-size: 14px !important;
    }
    
    /* Time stamps and metadata */
    .timestamp {
        color: #666;
    }
    
    /* New chat button */
    .new-chat-button {
        margin: 8px;
        padding: 8px 16px;
        background: white;
        border: 1px solid #E8E8E8;
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        cursor: pointer;
        transition: all 0.2s;
    }
    .new-chat-button:hover {
        background: #F0F0F0;
        border-color: #DDD;
    }
</style>
"""

"""Styles for the sidebar components."""

SIDEBAR_STYLE = """
<style>
div[data-testid="stSliderThumbValue"] {
    font-size: 9px !important;
}
div[data-testid="stSliderTickBar"] > div {
    font-size: 9px !important;
}
</style>
"""

import streamlit as st
import streamlit.components.v1 as components

def change_widget_font_size(widget_text, font_size='12px'):
    """Change the font size of a Streamlit widget by its label text.
    
    Args:
        widget_text (str): The text label of the widget to target
        font_size (str): Font size in CSS units (default: '12px')
    """
    html_str = f"""
    <script>
    var elements = window.parent.document.querySelectorAll('p'), i;
    for (i = 0; i < elements.length; ++i) {{
        if (elements[i].textContent.includes('{widget_text}')) {{
            elements[i].style.fontSize = '{font_size}';
        }}
    }}
    </script>
    """
    components.html(html_str, height=0, width=0)

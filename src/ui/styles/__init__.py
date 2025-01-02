"""Style management for the UI."""

import os

def load_css(filename: str) -> str:
    """Load CSS file content."""
    css_path = os.path.join(os.path.dirname(__file__), filename)
    with open(css_path, "r", encoding="utf-8") as f:
        return f.read()

def get_all_styles() -> str:
    """Get all CSS styles combined."""
    styles = []
    #FIXME: for filename in ["base.css", "logs.css", "interactions.css", "sidebar.css"]:
    for filename in ["base.css", "logs.css", "interactions.css", "sidebar.css"]:
        styles.append(load_css(filename))
    return "\n".join(styles)

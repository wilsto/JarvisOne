"""User preferences builder component."""

import logging
from dataclasses import dataclass
from typing import Optional
import streamlit as st

logger = logging.getLogger(__name__)

@dataclass
class PreferencesConfig:
    """Configuration for preferences building."""
    creativity_level: int = 1  # 0=Strict, 1=Balanced, 2=Creative
    style_level: int = 1      # 0=Professional, 1=Casual, 2=Fun
    length_level: int = 1     # 0=Short, 1=Balanced, 2=Long
    debug: bool = False

class PreferencesBuilder:
    """Builds preferences section with consistent structure and formatting."""

    @staticmethod
    def build(config: Optional[PreferencesConfig] = None) -> str:
        """Build preferences section from session state or config.
        
        Args:
            config: Optional PreferencesConfig, if not provided uses session state
            
        Returns:
            str: Formatted preferences section
        """
        try:
            if not config:
                # Get values from session state
                creativity = st.session_state.get('llm_creativity', 1)
                style = st.session_state.get('llm_style', 1)
                length = st.session_state.get('llm_length', 1)
                config = PreferencesConfig(
                    creativity_level=creativity,
                    style_level=style,
                    length_level=length
                )
                
            if config.debug:
                logger.info("Building preferences with config: %s", config)
                
            from ..generic_prompts import (
                CREATIVITY_PROMPTS,
                STYLE_PROMPTS,
                LENGTH_MODIFIERS
            )
            
            sections = []
            
            if config.debug:
                sections.append("=== Preferences ===")
                
            sections.extend([
                f"Core characteristics:\n{CREATIVITY_PROMPTS[config.creativity_level]}",
                f"Communication style:\n{STYLE_PROMPTS[config.style_level]}",
                f"Response length guideline:\n{LENGTH_MODIFIERS[config.length_level]}"
            ])
            
            return "\n\n".join(sections)
            
        except Exception as e:
            logger.error("Error building preferences: %s", e)
            return ""

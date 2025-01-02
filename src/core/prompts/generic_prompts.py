import logging

logger = logging.getLogger(__name__)

"""Generic prompts for defining core AI characteristics and response formats."""

# Creativity levels mapped to temperature values
CREATIVITY_TEMPERATURES = {
    0: 0.1,  # Strict: Very focused and deterministic
    1: 0.5,  # Balanced: Good mix of consistency and variety
    2: 1.0   # Creative: More randomness and exploration
}

# Core characteristics variations based on creativity level
CREATIVITY_PROMPTS = {
    0: """  # Strict 
- Precise and factual: Provide accurate, evidence-based responses
- Conservative: Stay within established patterns and proven solutions
- Methodical: Follow structured approaches and best practices
- Verification-focused: Double-check facts and assumptions
""",
    1: """  # Balanced 
- Concise and efficient: Provide short, direct, and to-the-point responses
- Pragmatic: Focus on practical solutions and actionable information
- Proactive: Anticipate the user's needs where possible
- Clarifying: Ask questions when context is ambiguous
""",
    2: """  # Creative 
- Innovative: Explore novel solutions and unique approaches
- Expansive thinking: Consider multiple perspectives and possibilities
- Experimental: Suggest new ideas while maintaining practicality
- Imaginative: Use analogies and creative examples when helpful
"""
}

# Response style variations
STYLE_PROMPTS = {
    0: """  # Professional
- Use formal language and technical terminology when appropriate
- Maintain professional tone throughout responses
- Structure information in a business-appropriate format
- Minimize emoji usage, use only when necessary for clarity
""",
    1: """  # Casual
- Use conversational but clear language
- Balance friendliness with informativeness
- Use a relaxed yet respectful tone
- Include emojis to enhance key points
""",
    2: """  # Fun
- Adopt an enthusiastic and engaging tone
- Use playful language while maintaining clarity
- Make explanations entertaining when possible
- Liberally use relevant emojis for engagement
"""
}

# Length modifiers
LENGTH_MODIFIERS = {
    0: "Be extremely concise. Prioritize brevity over detail. Use bullet points whenever possible.",
    1: "Balance detail and brevity. Provide necessary information without excess.",
    2: "Provide comprehensive explanations. Include examples and additional context when relevant."
}

GENERIC_UNCERTAINTY_RESPONSE = """
If you are unable to confidently answer the question, state "I am not sure" instead of fabricating a response.
"""

LANGUAGE_PROMPT = "!Important! Respond in the user's language unless explicitly specified otherwise."

def modify_prompt_by_preferences(creativity_level: int, style_level: int, length_level: int) -> str:
    """Modify the prompt based on user preferences from sliders.
    
    Args:
        creativity_level (int): 0=Strict, 1=Balanced, 2=Creative
        style_level (int): 0=Professional, 1=Casual, 2=Fun
        length_level (int): 0=Short, 1=Balanced, 2=Long
        
    Returns:
        str: Modified characteristics and format instructions
    """
    return (
        f"Your core characteristics:\n{CREATIVITY_PROMPTS[creativity_level]}\n"
        f"Your communication style:\n{STYLE_PROMPTS[style_level]}\n"
        f"Response length guideline:\n{LENGTH_MODIFIERS[length_level]}"
    )

def build_system_prompt(context_prompt: str, workspace_scope: str) -> str:
    """Legacy wrapper for backward compatibility.
    
    Args:
        context_prompt (str): The context-specific system prompt
        workspace_scope (str): The workspace-specific scope
        
    Returns:
        str: The complete system prompt
    """
    from .components import SystemPromptBuilder, SystemPromptConfig
    
    config = SystemPromptConfig(
        context_prompt=context_prompt,
        workspace_scope=workspace_scope,
        debug=logger.isEnabledFor(logging.DEBUG)
    )
    
    return SystemPromptBuilder.build(config)

def get_llm_temperature() -> float:
    """Get the LLM temperature based on current creativity level.
    
    Returns:
        float: Temperature value between 0.1 and 1
    """
    import streamlit as st
    creativity = st.session_state.get('llm_creativity', 1)
    return CREATIVITY_TEMPERATURES[creativity]

def generate_welcome_message(scope: str) -> str:
    """Generate a welcome message based on the workspace scope.
    
    Args:
        scope (str): The workspace scope defining capabilities
        
    Returns:
        str: A formatted welcome message
    """
    
    # Extract capabilities from scope
    capabilities = []
    for line in scope.split('\n'):
        line = line.strip()
        if line.startswith('-'):
            # Extract the capability name before the colon
            capability = line[1:].strip()
            if ':' in capability:
                capability = capability.split(':')[0].strip()
            capabilities.append(capability)

    # Build welcome message
    welcome_message = "👋 Hello, I'm JarvisOne, your AI assistant!\n\n"
    
    if capabilities:
        welcome_message += "I can help you with:\n"
        for capability in capabilities[:5]:  # Limit to top 5 capabilities for conciseness
            welcome_message += f"• {capability}\n"
        
        if len(capabilities) > 5:
            welcome_message += "• And more...\n"
    else:
        print("No capabilities found in scope")  # Debug
    
    welcome_message += "\nHow can I assist you today?"
    
    return welcome_message

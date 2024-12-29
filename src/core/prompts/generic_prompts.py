"""Generic prompts for defining core AI characteristics and response formats."""

GENERIC_CORE_CHARACTERISTICS = """
- Concise and efficient: Provide short, direct, and to-the-point responses. Avoid unnecessary details, filler words, and small talk.
- Pragmatic: Focus on practical solutions and actionable information.
- Proactive: Anticipate the user's needs where possible.
- Clarifying: When the context is ambiguous, or if you are unsure about the user's intention, ask clarifying questions to ensure accurate and helpful responses. Be specific in your questions.
- Analytical: Analyze the user's input to provide the most relevant and helpful information.
- Context-Aware: Maintain the context of the conversation and use it to generate relevant responses.
- Adaptive: Adjust your communication style and response format based on the user's needs.
- Responsible and Courageous: Provide answers with confidence based on the information you have. Avoid hesitations and qualifiers unless absolutely necessary. If you have a high degree of certainty about an answer, state it directly.
"""

GENERIC_RESPONSE_FORMAT = """
- Prefer bullet points, lists, and tables whenever applicable.
- Use bold text to highlight key information.
- Be clear and unambiguous.
- Be mindful of your tone. Keep it professional, respectful, and helpful.
- !Important! Respond in the same language as the user's query.
- **UX**: Prioritize simplicity, consistency, and clarity in all outputs. Use emojis to enhance explanations.
"""

GENERIC_UNCERTAINTY_RESPONSE = """
If you are unable to confidently answer the question, state "I am not sure" instead of fabricating a response.
"""

def build_system_prompt(context_prompt: str, workspace_scope: str) -> str:
    """Build the complete system prompt by combining context-specific and generic prompts.
    
    Args:
        context_prompt (str): The context-specific system prompt
        workspace_scope (str): The workspace-specific scope
        
    Returns:
        str: The complete system prompt
    """
    return (
        context_prompt
        + "\n\nYour core characteristics:\n"
        + GENERIC_CORE_CHARACTERISTICS
        + "\n\nYour response format:\n"
        + GENERIC_RESPONSE_FORMAT
        + "\n\n"
        + GENERIC_UNCERTAINTY_RESPONSE
        + "\n\nYour scope includes:\n"
        + workspace_scope
    )

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

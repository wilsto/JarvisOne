"""Manager for Ollama LLM provider.

This module handles the configuration and management of locally installed Ollama models.
It provides functionality to:
- Detect installed Ollama models using the CLI
- Update the configuration with available models
- Manage model metadata (size, context length, etc.)

Example:
    ```python
    # Get list of installed models
    models = get_installed_models()
    
    # Update configuration with installed models
    config = {
        "Ollama (Local)": {
            "models": {},
            "default_model": None
        }
    }
    updated_config = update_ollama_config(config)
    ```

Note:
    This module requires Ollama to be installed and accessible via command line.
    For installation instructions, visit: https://ollama.ai/
"""

import subprocess
import json
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

def get_installed_models() -> List[Dict]:
    """Get list of installed Ollama models.
    
    This function executes the 'ollama list' command and parses its output to get
    information about locally installed models.
    
    Returns:
        List[Dict]: List of dictionaries containing model information:
            - name (str): Model name with tag (e.g., 'mistral:latest')
            - size (str): Model size (e.g., '4.1GB')
            - description (str): Model description
            - context_length (int): Maximum context length
            - local (bool): Always True for Ollama models
            
    Raises:
        subprocess.CalledProcessError: If the ollama command fails
        Exception: For any other unexpected errors
        
    Example:
        ```python
        models = get_installed_models()
        # Returns: [
        #     {
        #         "name": "mistral:latest",
        #         "size": "4.1GB",
        #         "description": "Modèle local Ollama",
        #         "context_length": 8192,
        #         "local": True
        #     }
        # ]
        ```
    """
    try:
        # Run ollama list command
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Parse the output
        models = []
        for line in result.stdout.strip().split('\n')[1:]:  # Skip header
            if line:
                parts = line.split()
                if len(parts) >= 2:
                    name = parts[0]
                    size = parts[1]
                    # Ensure model name is correctly formatted
                    if ':' not in name:
                        name = f"{name}:latest"
                    models.append({
                        "name": name,
                        "size": size,
                        "description": "Modèle local Ollama",
                        "context_length": 8192,  # Default context length
                        "local": True
                    })
        
        logger.info(f"Found Ollama models: {[m['name'] for m in models]}")
        return models
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get Ollama models: {e.stderr}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error getting Ollama models: {str(e)}")
        return []

def update_ollama_config(config: Dict) -> Dict:
    """Update Ollama configuration with installed models.
    
    This function retrieves the list of installed models and updates the provided
    configuration dictionary with model information. If models are found, it also
    sets the first model as the default.
    
    Args:
        config (Dict): Configuration dictionary containing Ollama provider settings.
            Must have an "Ollama (Local)" key.
            
    Returns:
        Dict: Updated configuration dictionary with installed models information
        
    Example:
        ```python
        config = {
            "Ollama (Local)": {
                "models": {},
                "default_model": None
            }
        }
        updated_config = update_ollama_config(config)
        # Returns: {
        #     "Ollama (Local)": {
        #         "models": {
        #             "mistral:latest": {
        #                 "name": "mistral:latest",
        #                 "description": "Modèle local Ollama",
        #                 "context_length": 8192,
        #                 "local": True,
        #                 "size": "4.1GB"
        #             }
        #         },
        #         "default_model": "mistral:latest"
        #     }
        # }
        ```
    """
    models = get_installed_models()
    
    if not models:
        logger.warning("No Ollama models found, using default configuration")
        return config
        
    # Create models dictionary
    models_dict = {
        model['name']: {
            "name": model['name'],
            "description": model['description'],
            "context_length": model['context_length'],
            "local": True,
            "size": model['size']
        }
        for model in models
    }
    
    # Update config
    if "Ollama (Local)" in config:
        config["Ollama (Local)"]["models"] = models_dict
        if models:  # Set first model as default if we found any
            config["Ollama (Local)"]["default_model"] = models[0]["name"]
            
    return config

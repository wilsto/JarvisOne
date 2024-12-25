"""Manager for Ollama LLM provider."""

import subprocess
import json
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

def get_installed_models() -> List[Dict]:
    """Get list of installed Ollama models."""
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
    """Update Ollama configuration with installed models."""
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

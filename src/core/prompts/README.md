# Prompt System Components 🔧

## Directory Structure

```
prompts/
├── __init__.py
├── assembler.py          # Main prompt assembler
├── generic_prompts.py    # Legacy prompt utilities
└── components/          # Individual components
    ├── __init__.py
    ├── system_prompt.py
    ├── workspace_context.py
    ├── rag_context.py
    └── preferences.py
```

## Quick Start

```python
from core.prompts.components import (
    SystemPromptBuilder,
    WorkspaceContextBuilder,
    RAGContextBuilder,
    PreferencesBuilder
)
from core.prompts.assembler import PromptAssembler

# Configure components
system_config = SystemPromptConfig(...)
workspace_config = WorkspaceContextConfig(...)
rag_config = RAGContextConfig(...)
preferences_config = PreferencesConfig(...)

# Assemble prompt
assembler_config = PromptAssemblerConfig(
    system_config=system_config,
    workspace_config=workspace_config,
    rag_config=rag_config,
    preferences_config=preferences_config
)
final_prompt = PromptAssembler.assemble(assembler_config)
```

## Component Design

Each component follows these principles:
- Single Responsibility Principle (SRP)
- Robust error handling
- Debug mode support
- Comprehensive testing

For detailed documentation, see [prompt_system.md](../../docs/prompt_system.md)

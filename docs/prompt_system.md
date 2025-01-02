# Prompt Building System Documentation 📝

## Overview

The JarvisOne prompt building system is a modular, extensible architecture for constructing AI prompts. It follows the Single Responsibility Principle (SRP) and provides robust error handling.

## Architecture

### Components

1. **SystemPromptBuilder**
   - Handles core system instructions
   - Manages workspace scope integration
   - Example:
   ```python
   config = SystemPromptConfig(
       context_prompt="Your core instructions...",
       workspace_scope="dev",
       debug=False
   )
   prompt = SystemPromptBuilder.build(config)
   ```

2. **WorkspaceContextBuilder**
   - Manages workspace-specific context
   - Supports both raw context and structured metadata
   - Example:
   ```python
   config = WorkspaceContextConfig(
       workspace_id="dev",
       metadata={"context": "Workspace specific context..."},
       debug=False
   )
   context = WorkspaceContextBuilder.build(config)
   ```

3. **RAGContextBuilder**
   - Handles Retrieval-Augmented Generation context
   - Formats multiple document sources
   - Example:
   ```python
   config = RAGContextConfig(
       query="user query",
       documents=[RAGDocument(content="...", metadata={"file_path": "..."})],
       debug=False
   )
   context = RAGContextBuilder.build(config)
   ```

4. **PreferencesBuilder**
   - Manages user interaction preferences
   - Supports creativity, style, and length settings
   - Example:
   ```python
   config = PreferencesConfig(
       creativity_level=1,  # 0=Strict, 1=Balanced, 2=Creative
       style_level=1,      # 0=Professional, 1=Casual, 2=Fun
       length_level=1,     # 0=Short, 1=Balanced, 2=Long
       debug=False
   )
   prefs = PreferencesBuilder.build(config)
   ```

### Assembler

The `PromptAssembler` combines all components into a final prompt:

```python
config = PromptAssemblerConfig(
    system_config=system_config,
    workspace_config=workspace_config,
    rag_config=rag_config,
    preferences_config=preferences_config,
    debug=False
)
final_prompt = PromptAssembler.assemble(config)
```

## Error Handling

The system implements robust error handling:
- All components catch exceptions and return empty strings
- Errors are logged with appropriate context
- Debug mode provides detailed logging

## Debug Mode

Enable debug mode in any component to see detailed section markers:
```python
config = SystemPromptConfig(..., debug=True)
```

Debug output includes:
- Section markers (e.g., "=== System Instructions ===")
- Component configuration details
- Error details when failures occur

## Integration

### With CoreAgent

The prompt system is integrated with CoreAgent:
```python
def _build_prompt(self, user_query: str, workspace_id: str = None, role_id: str = None) -> str:
    # Configure components
    system_config = SystemPromptConfig(...)
    # ... configure other components
    
    # Assemble final prompt
    assembler_config = PromptAssemblerConfig(...)
    return PromptAssembler.assemble(assembler_config)
```

### With Workspace Manager

Workspace context is automatically integrated:
```python
workspace_config = WorkspaceContextConfig(
    workspace_id=workspace_id,
    metadata=workspace_manager.get_current_context_prompt(),
    debug=False
)
```

## Best Practices

1. **Component Usage**
   - Keep components focused and single-purpose
   - Use debug mode during development
   - Handle component errors appropriately

2. **Configuration**
   - Always provide complete config objects
   - Use type hints for better IDE support
   - Set appropriate debug flags

3. **Error Handling**
   - Check component output for empty strings
   - Monitor logs for error messages
   - Use debug mode to diagnose issues

## Testing

Each component has comprehensive tests:
- Basic functionality
- Edge cases
- Error conditions
- Debug mode output

Run tests with:
```bash
pytest tests/core/prompts/
```

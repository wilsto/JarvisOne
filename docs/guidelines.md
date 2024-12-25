# **CRITICAL OPERATIONAL DIRECTIVES**

## SOLID Principles

### Single Responsibility Principle (SRP)
- Each module, class, or function should have ONE and only one reason to change
- Responsibilities should be clearly separated and encapsulated
- Examples of responsibilities:
  - Data access
  - Business logic
  - Error handling
  - Configuration management
  - UI rendering
- Signs of SRP violation:
  - A module handles multiple unrelated tasks
  - Changes in one feature require modifications in unrelated code
  - Complex initialization logic spread across multiple components
- How to apply SRP:
  - Create dedicated managers for specific concerns (e.g., LLMManager, ConfigManager)
  - Keep UI components focused on rendering
  - Separate data access from business logic
  - Centralize error handling and logging
  - Use dependency injection to manage dependencies

## Documentation and Maintenance

Documentation must be kept up-to-date and treated as the **source of truth** for all design and implementation decisions. Key files include `README.md` for an overview and setup instructions, and `roadmap.md` for roadmap. After implementing changes, update the documentation to reflect new features, fixes, and edge cases. Ensure that examples and usage instructions are clear and accessible to both users and contributors.
This organization is clearer and more maintainable, with:

- README as a simple entry point
- The roadmap as detailed technical documentation

## Non-Regressions

**NEVER** remove or modify existing functionality without explicit approval. Always propose changes in an additive manner to maintain backward compatibility. Before releasing updates, thoroughly test for regressions to ensure that all existing features continue to function as expected. Highlight any potential impacts during the review process and address them before deployment.

## Tech Stack

- Use Uv for Python development

## Command Execution

- **NEVER** directly execute terminal or shell commands.
- Always ask the user to execute the necessary commands.
- Provide clear and detailed instructions on the commands to be executed, their purpose, and any precautions to take.
- If a sequence of commands is necessary, present them step by step with explanations for each step.

## Code Style and Structure

- Write concise, technical TypeScript code with accurate examples
- Use functional and declarative programming patterns; avoid classes
- Prefer iteration and modularization over code duplication
- Use descriptive variable names with auxiliary verbs (e.g., isLoading, hasError)

## Naming Conventions

- Use snake_case for directories and modules (e.g., components/form_wizard)
- Favor explicit imports for functions and classes
- Use PascalCase for class names (e.g., VisaForm.py)
- Use snake_case for function and variable names (e.g., form_validator.py)
- For JavaScript/TypeScript:
  - Use camelCase for variables, functions, and methods
  - Use PascalCase for classes and React components
  - Use UPPER_CASE for constants

## Error Handling

- Implement proper error boundaries
- Log errors appropriately for debugging
- Provide user-friendly error messages
- Handle network failures gracefully

## Documentation

- Maintain clear README with setup instructions
- Don't include comments unless it's for complex logic
- Document permission requirements

# JarvisOne Project Structure

This document describes the purpose of each directory and file within the JarvisOne project.

## Root Directory (`JarvisOne/`)

### `main.py`

- **Purpose**: Serves as the application's entry point by initializing the Streamlit interface, setting up core services, and establishing the main chat loop.

### `config/`

- **Purpose**: Centralizes all configuration settings and workspace definitions to enable personalized behavior across different contexts.

  #### `config/config.yaml`

  - **Purpose**: Stores global application settings including API credentials, LLM configurations, and system parameters.

  #### `config/spaces/`

  - **Purpose**: Contains workspace-specific configurations for different usage contexts.

    ##### `coaching_config.yaml`

    - **Purpose**: Configures the coaching workspace with specific paths, search parameters, and metadata for professional coaching content.

    ##### `dev_config.yaml`

    - **Purpose**: Defines development workspace settings for code-related activities and project management.

    ##### `personal_config.yaml`

    - **Purpose**: Manages personal workspace configuration for individual tasks and content.

    ##### `work_config.yaml`

    - **Purpose**: Specifies workspace settings for work-related activities and documentation.

  Each workspace configuration includes:
  - Dedicated paths and search locations
  - Context-specific file type inclusions/exclusions
  - Metadata and tagging for content organization
  - Custom search parameters and filters

### `data/`

- **Purpose**: Manages persistent storage for application data, including conversation history, embeddings, and cached responses.

### `docs/`

- **Purpose**: Houses comprehensive project documentation, including setup guides, architecture decisions, and API references.

  #### `docs/everything.md`

  - **Purpose**: Details the integration with the Everything search tool, including CLI commands, parameters, and usage examples.

  #### `docs/configuration.md`

  - **Purpose**: Configuration guide and best practices

### `log/`

- **Purpose**: Maintains timestamped application logs for monitoring, debugging, and audit purposes.

### `src/`

- **Purpose**: Contains the application's source code, organized into logical modules based on functionality.

  #### `src/core/`

  - **Purpose**: Implements foundational services and interfaces that other modules depend on.

    ##### `src/core/providers/`

    - **Purpose**: Implements standardized interfaces for each LLM service (Gemini, ChatGPT-4, Ollama), handling their specific API requirements.

    ##### `src/core/database/`

    - **Purpose**: Provides a unified interface for data storage and retrieval operations.
    - **Best Practices**:
      - **SQLite Date/Time**: Store dates as TEXT in ISO-8601 format (YYYY-MM-DDTHH:MM:SS.mmmmmm+HH:MM)
      - **Schema Documentation**: Always comment date format in CREATE TABLE statements
      - **Validation**: Ensure dates are properly formatted before insertion

    ##### `src/core/analysis/`

    - **Purpose**: Processes and analyzes user inputs to extract intent and relevant context.

    ##### Core Modules

    - **core_agent.py**: Defines the base agent interface and shared agent behaviors
    - **llm_base.py**: Provides abstract interfaces for LLM integration
    - **llm_config.py**: Handles provider-specific configuration and validation
    - **llm_manager.py**: Coordinates LLM provider selection and request routing
    - **llm_utils.py**: Offers helper functions for LLM operations
    - **config_manager.py**: Loads and validates configuration settings
    - **workspace_manager.py**: Manages workspaces, their configurations, and system prompts

  #### `src/features/`

  - **Purpose**: Implements distinct application capabilities through specialized modules.

    ##### `src/features/agents/`

    - **Purpose**: Houses specialized AI agents, each focused on a specific type of user interaction.

      ###### `agent_orchestrator.py`

      - **Purpose**: Routes user requests to appropriate specialized agents based on intent analysis.

      ###### `chat_agent.py`

      - **Purpose**: Handles general conversation flow and maintains dialogue context.

      ###### `file_search_agent.py`

      - **Purpose**: Translates natural language queries into Everything search commands and formats results.

      ###### `query_analyzer_agent.py`

      - **Purpose**: Determines user intent and extracts key parameters from natural language inputs.

    ##### `src/features/chat_processor.py`

    - **Purpose**: Manages message flow, history, and state in the chat interface.

  #### `src/rag/`

  - **Purpose**: Implements Retrieval-Augmented Generation (RAG) functionality for enhanced context-aware responses.

    #### `document_processor.py`

    - **Purpose**: Handles document processing, chunking, embedding generation, and vector storage using ChromaDB.
    - **Key Components**:
      - `DocumentProcessor`: Core class managing document processing and vector operations
      - Importance-based document classification (High/Medium/Low/Excluded)
      - Workspace isolation for document collections
      - Asynchronous processing capabilities
      - Semantic search functionality

    #### `data/vector_db/`

    - **Purpose**: Persistent storage for document embeddings and vector indices
    - Organized by workspace for isolated document management
    - Uses ChromaDB for efficient vector storage and retrieval

    ### `src/rag/document_handlers/`

    - **Purpose**: Provides document handlers for different file types.

    - `base_handler.py`: Base class for document handlers
    - `text_handler.py`: Handler for text files (TXT, JSON, MD)
    - `markitdown_handler.py`: Handler for Office documents
    - `epub_handler.py`: Handler for EPUB e-books

    ### `src/rag/document_watcher/`

    - **Purpose**: Monitors file system changes and manages document tracking.

    - `document_tracker.py`:
      - SQLite-based document tracking
      - Status tracking (pending/processed/error/deleted)
      - Hash-based change detection
      - Thread-safe database operations

    - `watcher.py`:
      - File system monitoring using Watchdog
      - Intelligent file scanning with change detection
      - Only updates documents when:
        - File is new (not in database)
        - File has changed (different hash)
        - File was previously deleted but exists again
      - Supports workspace isolation
      - Handles supported file extensions only

    - `workspace_watcher.py`:
      - Manages workspace-specific file watchers
      - Coordinates document tracking across workspaces
      - Handles watcher lifecycle (start/stop)

    ### `src/rag/enhancer.py`

    - **Purpose**: Enhances prompts with document context

    ### `src/rag/middleware.py`

    - **Purpose**: RAG processing middleware

    ### `src/rag/processor.py`

    - **Purpose**: Message processing interface

    ### `src/rag/query_handler.py`

    - **Purpose**: Handles RAG queries

  #### `src/ui/`

  - **Purpose**: Implements the Streamlit-based user interface components.

    ##### `src/ui/components/`

    - **Purpose**: Provides reusable UI elements like message bubbles and input fields.

    ##### `src/ui/interactions/`

    - **Purpose**: Handles user input events and UI state management.

    - `base.py`: Base interaction display class
    - `agents/`: Agent-specific interaction handlers
      - `chat.py`: Chat agent interactions
      - `file_search.py`: File search interactions

    ##### `src/ui/styles/`

    - **Purpose**: Defines consistent visual styling through CSS and Streamlit theme configurations.

    ##### UI Core Files

    - **apps.py**: Configures the main Streamlit application layout
    - **chat_ui.py**: Implements the chat interface components
    - **parameters.py**: Defines UI-specific configuration parameters

  #### `src/utils/`

  - **Purpose**: Provides shared utility functions used across multiple modules.

    ##### `src/utils/logging_config.py`

    - **Purpose**: Establishes consistent logging patterns and output formats.

  #### `src/types/`

  - **Purpose**: Defines data structures and type hints for maintaining code consistency.

### `tests/`

- **Purpose**: Ensures code quality through comprehensive testing.

  #### `tests/integration/`

  - **Purpose**: Contains integration tests that verify component interactions and system behavior.

  #### `tests/unit/`

  - **Purpose**: Contains unit tests that verify individual component behavior in isolation.

  #### `tests/utils.py`

  - **Purpose**: Provides common testing utilities and mock objects.

  #### `tests/conftest.py`

  - **Purpose**: Defines shared test fixtures and configuration.

## New Components

### Interactions

- `ui/interactions/`: Base classes and handlers for UI interactions

### Configuration

- `.env.example`: Template for environment variables (API keys)

## Tech Stack

- **Python**: Use Uv, Python 3.12.
- **Streamlit**: Version 1.31+ for UI.
- **LLMs**: Gemini 2.0, ChatGPT-4, Ollama, Anthropic.
- **Testing**: Pytest + Streamlit Testing.
- **Config**: ruamel.yaml.
- **RAG Stack**:
  - LangChain for text processing
  - SentenceTransformers for embeddings
  - ChromaDB for vector storage
- **Future Technologies**: GTTS/SpeechRecognition for future voice capabilities.

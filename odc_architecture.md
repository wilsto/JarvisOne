# **JarvisOne Architecture Objectives, Dependencies, and Constraints (ODC)**

## Architectural Objectives

* **Modularity:**
  * Design a modular architecture to facilitate the addition of new features and system evolution.
  * The architecture should be extensible to integrate new LLMs or external tools.
* **Adaptability:**
  * The architecture should allow connecting different data sources.
* **Security:**
  * The architecture must ensure secure access to the system and its data.
* **Performance:**
  * Design an architecture that minimizes response time.
* **Reusability:**
  * Components should be reusable as much as possible.
* **Maintainability:**
  * The architecture should be easy to understand and maintain by other developers.

## Architectural Dependencies

* **Layered Architecture:**
  * The architecture is organized in layers for a clear separation of concerns.
* **Workflow:**
  * The user request is processed according to a specific flow.
* **Agents:**
  * Intelligent agents handle request analysis and interaction with external tools.
  * `query_analyzer_agent.py` for query analysis.
  * `file_search_agent.py` for interaction with the `everything` tool.
* **User Interface (UI):**
  * Streamlit's text input for user inputs.
  * Native interfaces of external tools for displaying results when available.
  * A flexible interface adapts based on the tools used.
* **System Prompts:**
  * Each workspace utilizes a system prompt to guide the agent's behavior and expertise.

## Architectural Constraints

* **Modularity:**
  * Modularity must be maintained during new feature implementation.
* **Performance:**
  * The architecture must minimize execution latency.
* **Security:**
  * The architecture must minimize security risks (data access, access to LLMs).
* **External Tools:**
  * Use external tool interfaces to display results.
  * Avoid reimplementing existing functionalities.
  * Use of an interaction for each usage of an external tool.

## Core File Structure

JarvisOne/
├── main.py                   # Main entry point
├── config/                   # Configuration files
│   └── config.yaml          # Main configuration file
├── data/                    # Data and embeddings
├── docs/                    # Documentation
│   └── everything.md        # Everything CLI documentation
├── log/                     # Log files
├── src/                     # Main source code
│   ├── core/               # Core logic
│   │   ├── llm_providers/  # LLM-specific implementations
│   │   ├── interfaces/     # Common interfaces and protocols
│   │   ├── security/      # Input validation and guardrails
│   │   └── config_manager.py
│   ├── agents/            # LLM agents (moved to top-level)
│   │   ├── file_search_agent.py
│   │   └── query_analyzer_agent.py
│   ├── services/          # Business logic services
│   │   ├── file_search.py
│   │   └── document_manager.py
│   ├── ui/               # UI components
│   │   ├── components/   # Reusable UI elements
│   │   ├── pages/       # Page-specific components
│   │   └── styles/      # UI styling
│   ├── types/           # Types and schemas
│   └── utils/           # Utilities
│       └── logging_config.py

## Architectural Logic

### Core Processing Flow

1. **User Query**: The user submits a query using natural language via the chat interface.
2. **Agent Interaction**: An intelligent agent processes the query and identifies actions required.
3. **Data Access**: Data is retrieved from various data sources.
4. **Tool Interaction**: External tool interfaces are used to perform actions and display their results.
5. **Response Generation**: A language model generates a response.
6. **Interaction Handling**: The response is displayed via an interaction in the UI
7. **Final Response**: The user receives the final response in the chat.

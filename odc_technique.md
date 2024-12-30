# **JarvisOne Technical Objectives, Dependencies, and Constraints (ODC)**

## Technical Objectives

* **Core Functionality:**
  * Enable natural language interaction via a chat interface.
  * Integrate external tools for specific functionalities (e.g., file search).
  * Display external tool output using their native interfaces when appropriate.
* **Request Processing:**
  * Retrieve user requests via the Streamlit chat interface.
  * Perform a quick lookup in a local cache for previous responses.
  * Analyze and extract relevant information from requests.
  * Apply input safeguards (e.g., PII redaction).
  * Access persistent data (documents, tables, etc.).
  * Manage access to different LLMs.
  * Generate responses using the selected model.
  * Evaluate the quality of the generated response.
  * Apply output safeguards (safe, ethical).
  * Cache responses for future reuse.
* **User Interface (UI) Management:**
  * Use a text input component for users to submit requests.
  * Display file search results using the `Everything` interface.
  * Display remaining outputs in the chat interface.
* **External Tool Integration:**
  * Ability to integrate and execute diverse external tools as needed.
  * Use native interfaces of external tools when available.
* **Language and Platform:**
  * Develop with Python 3.12.
  * Use Streamlit 1.31+ for the user interface.
  * Use intelligent agents for agent management.
  * Use advanced LLMs for natural language processing.

## Technical Dependencies

* **Software and Libraries:**
  * Python 3.12.
  * Streamlit 1.31+.
  * `Everything` for file search.
* **External Tools:**
  * `C:\Program Files\Everything\es.exe` (specific path for executing `Everything`).
  * `Everything` interface for displaying results.
* **Configuration Files**:
  * Project base configuration is done through YAML configuration files.

## Technical Constraints

* **Performance:**
  * Response time to a request must be as fast as possible.
* **Security:**
  * Protection against PII in user requests.
  * Secure management of access to LLMs (tokens).
  * Filtering output to ensure it is safe and ethical.
* **User Interface (UI):**
  * Utilize external tool interfaces when available (e.g., `Everything`).
  * Display the remaining results in the chat interface.
  * The interface layout must be simple and responsive.
  * Avoid reimplementing display or interaction systems that already exist in external tools.
* **Caching:**
  * Local caching mechanism must be implemented to optimize response time.
* **Documentation**:
  * The project's documentation should be simple, maintainable, and updated with each system change.
* **Configuration:**
  * Project base configuration is done through YAML configuration files.
* **System Prompts:**
  * System prompts are used to guide the behavior of the AI agents for each workspace.

## Document Processing

### Supported Document Types
- **Text Files**: `.txt`, `.json`, `.md`, `.markdown`
- **Office Documents**: `.pdf`, `.docx`, `.xlsx`, `.pptx` (via MarkItDown)
- **E-Books**: `.epub`

### Document Handlers
- **TextHandler**: Processes plain text files, JSON, and Markdown
- **MarkItDownHandler**: Converts Office documents to text
- **EpubHandler**: Extracts text from EPUB e-books

### Processing Strategy
- Each handler validates file size and type
- Text extraction preserves relevant content
- Documents are chunked and embedded for search

## RAG Implementation

### Document Processing

- **Chunking Strategy**
  - Use RecursiveCharacterTextSplitter for consistent text segmentation
  - Chunk size and overlap parameters must be tuned for optimal retrieval
  - Handle empty files and invalid content gracefully

### Vector Storage

- **ChromaDB Integration**
  - Persistent storage in workspace-specific collections
  - Efficient embedding storage and retrieval
  - Thread-safe operations for concurrent processing

### Performance Considerations

- **Asynchronous Processing**
  - Document processing runs in separate threads
  - Non-blocking operations for UI responsiveness
  - Optional wait-for-completion functionality

### Security & Isolation

- **Workspace Separation**
  - Strict isolation between workspace collections
  - No cross-contamination of document embeddings
  - Importance-level based document classification

### Dependencies

- **Core Libraries**
  - LangChain for text processing
  - SentenceTransformers for embedding generation
  - ChromaDB for vector storage

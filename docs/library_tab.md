# Library Tab Documentation

## Overview
The Library Tab provides a document management interface within JarvisOne, allowing users to browse, search, and interact with documents in their workspace.

## Components

### Document Service
- Manages document operations and workspace integration
- Handles document retrieval and filtering
- Maintains workspace context awareness

### Search Functionality
- Real-time document search
- File type filtering
- Workspace-aware results

### Document Interactions
- File type icons for visual recognition
- Open file location functionality
- Document settings and metadata view
- Path copying capability

## Usage

### Searching Documents
1. Use the search bar to find documents by name or content
2. Filter results by file type using the dropdown
3. Results update automatically as you type

### Document Actions
- Click the folder icon (📁) to open file location
- Click the settings icon (⚙️) to view document details
- Use the settings panel to:
  - View full path
  - Check file size and modification date
  - Copy file path
  - Open file location

### Workspace Integration
- Documents are automatically filtered by current workspace
- Document count shows total files in workspace
- All operations respect workspace boundaries

## Testing
Run tests using pytest:
```bash
pytest tests/features/ui/document/
```

## Dependencies
- Streamlit 1.31+
- Python 3.12
- Windows OS (for file location opening)

"""Tests for different document types processing."""

import pytest
from pathlib import Path
from src.rag.document_processor import DocumentProcessor

# Path to test files directory
TEST_FILES_DIR = Path(__file__).parent / "test_files"

# List of all test files and their expected content
TEST_FILES = [
    # Text Handler files
    ("sample.txt", "This is a sample text file"),
    ("sample.json", "Sample JSON Document"),
    ("sample.md", "Sample Markdown Document"),
    
    # MarkItDown Handler files
    ("sample.pdf", "Sample PDF Document"),
    ("sample.docx", "Sample DOCX Document"),
    ("sample.xlsx", "Sample XLSX Document"),
    ("sample.pptx", "Sample PPTX Document"),
    
    # EPUB Handler files
    ("sample.epub", "Sample EPUB Document"),
]

@pytest.fixture
def doc_processor(tmp_path):
    """Create a DocumentProcessor instance."""
    return DocumentProcessor(vector_db_path=str(tmp_path))

def verify_document_processing(doc_processor, file_path: Path, expected_content: str):
    """Helper function to verify document processing."""
    workspace_id = "test_workspace"
    
    # Process the document
    doc_processor.process_document(
        str(file_path),
        workspace_id=workspace_id,
        vector_db_path=str(TEST_FILES_DIR),
        importance_level="High"
    )
    
    # Verify content was processed
    collection = doc_processor._get_collection(workspace_id)
    results = collection.query(
        query_texts=[expected_content],
        n_results=1
    )
    
    assert len(results['documents']) > 0
    assert expected_content.lower() in results['documents'][0][0].lower()
    
    # Verify metadata
    metadata = results['metadatas'][0][0]
    assert metadata['file_name'] == file_path.name
    assert metadata['file_type'] == file_path.suffix.lower()
    assert metadata['importance_level'] == "High"

# Tests for Text Handler
def test_text_processing(doc_processor):
    """Test processing of plain text files."""
    file_path = TEST_FILES_DIR / "sample.txt"
    verify_document_processing(
        doc_processor,
        file_path,
        "This is a sample text file"
    )

def test_json_processing(doc_processor):
    """Test processing of JSON files."""
    file_path = TEST_FILES_DIR / "sample.json"
    verify_document_processing(
        doc_processor,
        file_path,
        "Sample JSON Document"
    )

def test_markdown_processing(doc_processor):
    """Test processing of Markdown files."""
    file_path = TEST_FILES_DIR / "sample.md"
    verify_document_processing(
        doc_processor,
        file_path,
        "Sample Markdown Document"
    )

# Tests for MarkItDown Handler
def test_pdf_processing(doc_processor):
    """Test processing of PDF files."""
    file_path = TEST_FILES_DIR / "sample.pdf"
    verify_document_processing(
        doc_processor,
        file_path,
        " thérapie des schémas"
    )

def test_docx_processing(doc_processor):
    """Test processing of DOCX files."""
    file_path = TEST_FILES_DIR / "sample.docx"
    verify_document_processing(
        doc_processor,
        file_path,
        "Sample DOCX Document"
    )

def test_xlsx_processing(doc_processor):
    """Test processing of XLSX files."""
    file_path = TEST_FILES_DIR / "sample.xlsx"
    verify_document_processing(
        doc_processor,
        file_path,
        "Sample XLSX Document"
    )

def test_pptx_processing(doc_processor):
    """Test processing of PPTX files."""
    file_path = TEST_FILES_DIR / "sample.pptx"
    verify_document_processing(
        doc_processor,
        file_path,
        "Sample PPTX Document"
    )

# Tests for EPUB Handler
def test_epub_processing(doc_processor):
    """Test processing of EPUB files."""
    file_path = TEST_FILES_DIR / "sample.epub"
    verify_document_processing(
        doc_processor,
        file_path,
        "Sample EPUB Document"
    )

#FIXME:  AssertionError: Content not found for sample.json: expected 'Sample JSON Document' in chunks: ['This is a sample text file']
def test_batch_processing(doc_processor):
    """Test processing multiple documents of different types."""
    workspace_id = "test_workspace"
    
    # Process all files
    for filename, expected_content in TEST_FILES:
        file_path = TEST_FILES_DIR / filename
        doc_processor.process_document(
            str(file_path),
            workspace_id=workspace_id,
            vector_db_path=str(TEST_FILES_DIR),
            importance_level="High"
        )
    
    # Verify all documents were processed
    collection = doc_processor._get_collection(workspace_id)
    
    # Test each file individually to ensure proper content matching
    for filename, expected_content in TEST_FILES:
        results = collection.query(
            query_texts=[expected_content],
            n_results=5  # Augmenté pour avoir plus de résultats
        )
        assert len(results['documents']) > 0
        
        # Cherche le contenu attendu dans tous les chunks retournés
        found = False
        for chunks in results['documents'][0]:
            if expected_content.lower() in chunks.lower():
                found = True
                break
                
        assert found, f"Content not found for {filename}: expected '{expected_content}' in chunks: {results['documents'][0]}"

def test_unsupported_file(doc_processor):
    """Test handling of unsupported file types."""
    file_path = TEST_FILES_DIR / "sample.unsupported"
    with open(file_path, 'w') as f:
        f.write("Test content")
    
    with pytest.raises(ValueError, match="No handler found for file"):
        doc_processor.process_document(
            str(file_path),
            workspace_id="test_workspace",
            vector_db_path=str(TEST_FILES_DIR)
        )

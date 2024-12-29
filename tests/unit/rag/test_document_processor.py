"""Tests for the document processor module."""

import os
import tempfile
import time
import pytest
from src.rag.document_processor import DocumentProcessor, process_text_file
from pathlib import Path


@pytest.fixture
def temp_vector_db():
    """Fixture to create a temporary vector DB directory."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Give ChromaDB time to close connections
    time.sleep(0.1)
    try:
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
    except Exception as e:
        print(f"Error cleaning up temp dir: {e}")

@pytest.fixture
def sample_text_file():
    """Fixture to create a temporary text file with sample content."""
    content = """This is a sample text file for testing.
    It contains multiple lines of text.
    We will use this to test our document processing functionality.
    The text should be long enough to create multiple chunks.
    """ * 10  # Repeat to ensure we get multiple chunks
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(content)
        temp_file_path = f.name
    
    yield temp_file_path
    
    # Cleanup
    try:
        os.unlink(temp_file_path)
    except FileNotFoundError:
        pass

@pytest.fixture
def processor(temp_vector_db):
    """Fixture to create a DocumentProcessor instance."""
    processor = DocumentProcessor(temp_vector_db)
    yield processor
    processor.cleanup()

def test_document_processor_initialization(processor):
    """Test DocumentProcessor initialization."""
    assert processor.vector_db_path == Path(processor.vector_db_path)
    assert processor.text_splitter is not None
    assert processor.embeddings is not None

def test_process_text_file_basic(temp_vector_db, sample_text_file):
    """Test basic text file processing."""
    workspace_id = "test_workspace"
    
    # Process the file and wait for completion
    process_text_file(
        file_path=sample_text_file,
        workspace_id=workspace_id,
        vector_db_path=temp_vector_db,
        wait_for_completion=True
    )
    
    # Verify the workspace directory was created
    workspace_path = Path(temp_vector_db) / workspace_id
    assert workspace_path.exists()
    assert workspace_path.is_dir()
    
    # Verify ChromaDB files were created
    assert any(workspace_path.iterdir()), "Vector DB files should be created"
    
    # Verify documents were added by creating a new processor
    processor = DocumentProcessor(temp_vector_db)
    client = processor._get_chroma_client(workspace_id)
    collection = client.get_or_create_collection("documents")
    docs = collection.get()
    assert docs['documents'], "Documents should be stored in the collection"

def test_process_text_file_chunking(temp_vector_db, processor):
    """Test that text is properly chunked."""
    # Create a text file with content that should generate multiple chunks
    content = "This is a test sentence that should be long enough to split into chunks. " * 50
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(content)
        temp_file_path = f.name
    
    try:
        # Process using the processor directly
        processor._process_file_internal(
            file_path=temp_file_path,
            workspace_id="test_workspace",
            importance_level="Medium"
        )
        
        # Get collection from same processor
        collection = processor._get_chroma_client("test_workspace").get_or_create_collection("documents")
        
        # Get all documents
        docs = collection.get()
        
        # Debug output
        print(f"Found {len(docs['documents'])} documents")
        if docs['documents']:
            print(f"First document length: {len(docs['documents'][0])}")
        
        # Verify multiple chunks were created
        assert len(docs['documents']) > 1, "Text should be split into multiple chunks"
        
    finally:
        try:
            os.unlink(temp_file_path)
        except FileNotFoundError:
            pass

def test_process_text_file_metadata(temp_vector_db, sample_text_file, processor):
    """Test that metadata is properly stored."""
    workspace_id = "test_workspace"
    importance = "High"
    
    # Process using the processor directly
    processor._process_file_internal(
        file_path=sample_text_file,
        workspace_id=workspace_id,
        importance_level=importance
    )
    
    # Get collection from same processor
    collection = processor._get_chroma_client(workspace_id).get_or_create_collection("documents")
    
    # Verify metadata
    docs = collection.get()
    assert docs['metadatas'], "Should have metadata"
    for metadata in docs['metadatas']:
        assert metadata['workspace_id'] == workspace_id
        assert metadata['importance_level'] == importance
        assert metadata['file_path'] == sample_text_file
        assert 'chunk_index' in metadata

def test_process_text_file_empty(temp_vector_db, processor):
    """Test processing an empty file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        temp_file_path = f.name
    
    try:
        # Process using the processor directly
        processor._process_file_internal(
            file_path=temp_file_path,
            workspace_id="test_workspace",
            importance_level="Medium"
        )
        
        # Verify workspace directory exists
        workspace_path = Path(temp_vector_db) / "test_workspace"
        assert workspace_path.exists(), "Workspace directory should be created"
        assert workspace_path.is_dir(), "Workspace path should be a directory"
        
    finally:
        try:
            os.unlink(temp_file_path)
        except FileNotFoundError:
            pass

def test_process_text_file_invalid_path(temp_vector_db):
    """Test processing with invalid file path."""
    with pytest.raises(FileNotFoundError):
        process_text_file(
            file_path="nonexistent_file.txt",
            workspace_id="test_workspace",
            vector_db_path=temp_vector_db,
            wait_for_completion=True  # Wait for the error to propagate
        )

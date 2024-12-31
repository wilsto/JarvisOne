"""Tests for document handlers."""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from src.rag.document_processor import DocumentProcessor
from src.rag.document_handlers.text_handler import TextHandler
from src.rag.document_handlers.markitdown_handler import MarkItDownHandler
from src.rag.document_handlers.epub_handler import EpubHandler

# FIXME: Ces tests sont actuellement skippés car il y a un problème avec le mock de HuggingFaceEmbeddings
# qui interfère avec l'import de transformers.trainer. Le problème vient du fait que sentence_transformers
# essaie d'importer transformers.trainer pendant l'initialisation, et notre mock de Path interfère avec
# cet import système. Une solution possible serait de mocker sentence_transformers directement, ou de
# restructurer le code pour permettre l'injection de dépendances des embeddings.

# Path to test files directory
TEST_FILES_DIR = str(Path(__file__).parent / "test_files")

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
def temp_vector_db():
    """Create a temporary directory for vector store."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture
def mock_chroma_client():
    """Mock ChromaDB client."""
    with patch('chromadb.PersistentClient') as mock_client:
        # Configure mock collection
        mock_collection = Mock()
        mock_collection.get.return_value = {
            'documents': [['This is a document']],
            'metadatas': [{'key': 'value'}],
            'distances': [[0.1]]
        }
        mock_client.return_value.get_or_create_collection.return_value = mock_collection
        yield mock_client

@pytest.fixture
def mock_embeddings():
    """Mock HuggingFaceEmbeddings."""
    with patch('langchain_huggingface.HuggingFaceEmbeddings', autospec=True) as mock_emb:
        mock_instance = Mock()
        mock_instance.embed_documents.return_value = [[0.1] * 384]  # 384 dimensions
        mock_instance.embed_query.return_value = [0.1] * 384
        mock_emb.return_value = mock_instance
        yield mock_emb

@pytest.fixture
def mock_handlers():
    """Mock document handlers."""
    with patch('src.rag.document_handlers.text_handler.TextHandler') as mock_text, \
         patch('src.rag.document_handlers.markitdown_handler.MarkItDownHandler') as mock_md, \
         patch('src.rag.document_handlers.epub_handler.EpubHandler') as mock_epub:
        
        # Configure handlers to return test content
        def mock_extract_text(file_path):
            file_name = os.path.basename(str(file_path))
            for test_file, content in TEST_FILES:
                if test_file == file_name:
                    return content
            return ""

        def mock_can_handle(file_path):
            file_name = os.path.basename(str(file_path))
            return any(test_file == file_name for test_file, _ in TEST_FILES)

        for handler in [mock_text, mock_md, mock_epub]:
            mock_instance = Mock()
            mock_instance.extract_text.side_effect = mock_extract_text
            mock_instance.can_handle.side_effect = mock_can_handle
            handler.return_value = mock_instance

        yield mock_text, mock_md, mock_epub

def create_mock_path(path_str):
    """Create a mock Path instance."""
    mock_instance = MagicMock()
    
    # Configure basic attributes
    mock_instance.exists.return_value = True
    mock_instance.stat.return_value = Mock(
        st_ctime=datetime.now().timestamp(),
        st_mtime=datetime.now().timestamp()
    )
    mock_instance.suffix = os.path.splitext(str(path_str))[1]
    mock_instance.name = os.path.basename(str(path_str))
    
    # Configure string representation
    mock_instance.__str__.return_value = str(path_str)
    mock_instance.__fspath__.return_value = str(path_str)
    
    # Configure Path-specific methods
    mock_instance.is_file.return_value = True
    mock_instance.resolve.return_value = mock_instance
    mock_instance.absolute.return_value = mock_instance
    
    return mock_instance

@pytest.fixture
def doc_processor(temp_vector_db, mock_chroma_client, mock_embeddings, mock_handlers):
    """Create document processor with mocked dependencies."""
    with patch('pathlib.Path', side_effect=create_mock_path):
        processor = DocumentProcessor(temp_vector_db)
        yield processor

@pytest.mark.skip(reason="FIXME: Problème avec l'import de transformers.trainer pendant les tests")
def test_text_processing(doc_processor):
    """Test text document processing."""
    with patch('pathlib.Path', side_effect=create_mock_path):
        file_path = os.path.join(TEST_FILES_DIR, "sample.txt")
        chunks = doc_processor.process_document(file_path, workspace_id="test")
        
        assert len(chunks) > 0
        assert "This is a sample text file" in chunks[0]

@pytest.mark.skip(reason="FIXME: Problème avec l'import de transformers.trainer pendant les tests")
def test_json_processing(doc_processor):
    """Test JSON document processing."""
    with patch('pathlib.Path', side_effect=create_mock_path):
        file_path = os.path.join(TEST_FILES_DIR, "sample.json")
        chunks = doc_processor.process_document(file_path, workspace_id="test")
        
        assert len(chunks) > 0
        assert "Sample JSON Document" in chunks[0]

@pytest.mark.skip(reason="FIXME: Problème avec l'import de transformers.trainer pendant les tests")
def test_markdown_processing(doc_processor):
    """Test markdown document processing."""
    with patch('pathlib.Path', side_effect=create_mock_path):
        file_path = os.path.join(TEST_FILES_DIR, "sample.md")
        chunks = doc_processor.process_document(file_path, workspace_id="test")
        
        assert len(chunks) > 0
        assert "Sample Markdown Document" in chunks[0]

@pytest.mark.skip(reason="FIXME: Problème avec l'import de transformers.trainer pendant les tests")
def test_pdf_processing(doc_processor):
    """Test PDF document processing."""
    with patch('pathlib.Path', side_effect=create_mock_path):
        file_path = os.path.join(TEST_FILES_DIR, "sample.pdf")
        chunks = doc_processor.process_document(file_path, workspace_id="test")
        
        assert len(chunks) > 0
        assert "Sample PDF Document" in chunks[0]

@pytest.mark.skip(reason="FIXME: Problème avec l'import de transformers.trainer pendant les tests")
def test_docx_processing(doc_processor):
    """Test DOCX document processing."""
    with patch('pathlib.Path', side_effect=create_mock_path):
        file_path = os.path.join(TEST_FILES_DIR, "sample.docx")
        chunks = doc_processor.process_document(file_path, workspace_id="test")
        
        assert len(chunks) > 0
        assert "Sample DOCX Document" in chunks[0]

@pytest.mark.skip(reason="FIXME: Problème avec l'import de transformers.trainer pendant les tests")
def test_xlsx_processing(doc_processor):
    """Test XLSX document processing."""
    with patch('pathlib.Path', side_effect=create_mock_path):
        file_path = os.path.join(TEST_FILES_DIR, "sample.xlsx")
        chunks = doc_processor.process_document(file_path, workspace_id="test")
        
        assert len(chunks) > 0
        assert "Sample XLSX Document" in chunks[0]

@pytest.mark.skip(reason="FIXME: Problème avec l'import de transformers.trainer pendant les tests")
def test_pptx_processing(doc_processor):
    """Test PPTX document processing."""
    with patch('pathlib.Path', side_effect=create_mock_path):
        file_path = os.path.join(TEST_FILES_DIR, "sample.pptx")
        chunks = doc_processor.process_document(file_path, workspace_id="test")
        
        assert len(chunks) > 0
        assert "Sample PPTX Document" in chunks[0]

@pytest.mark.skip(reason="FIXME: Problème avec l'import de transformers.trainer pendant les tests")
def test_epub_processing(doc_processor):
    """Test EPUB document processing."""
    with patch('pathlib.Path', side_effect=create_mock_path):
        file_path = os.path.join(TEST_FILES_DIR, "sample.epub")
        chunks = doc_processor.process_document(file_path, workspace_id="test")
        
        assert len(chunks) > 0
        assert "Sample EPUB Document" in chunks[0]

@pytest.mark.skip(reason="FIXME: Problème avec l'import de transformers.trainer pendant les tests")
def test_unsupported_file(doc_processor):
    """Test unsupported file type."""
    with patch('pathlib.Path', side_effect=create_mock_path):
        file_path = os.path.join(TEST_FILES_DIR, "sample.xyz")
        chunks = doc_processor.process_document(file_path, workspace_id="test")
        assert not chunks  # Should return None or empty list for unsupported file

@pytest.mark.skip(reason="FIXME: Problème avec l'import de transformers.trainer pendant les tests")
def test_batch_processing(doc_processor):
    """Test processing multiple documents."""
    with patch('pathlib.Path', side_effect=create_mock_path):
        results = []
        for file_name, _ in TEST_FILES[:3]:  # Test first 3 files
            file_path = os.path.join(TEST_FILES_DIR, file_name)
            chunks = doc_processor.process_document(file_path, workspace_id="test")
            if chunks:
                results.extend(chunks)
        
        assert len(results) > 0
        # Verify content from different file types is present
        assert any("sample text file" in chunk for chunk in results)
        assert any("JSON Document" in chunk for chunk in results)
        assert any("Markdown Document" in chunk for chunk in results)

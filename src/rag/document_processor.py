"""Process and manage documents for RAG."""

import os
import logging
import queue
from datetime import datetime
from pathlib import Path
from typing import Optional, Literal, Dict, Any, List
from langchain.text_splitter import RecursiveCharacterTextSplitter
import hashlib

from vector_db.manager import VectorDBManager
from .document_handlers import (
    BaseDocumentHandler,
    MarkItDownHandler,
    TextHandler,
    EpubHandler
)

logger = logging.getLogger(__name__)

ImportanceLevelType = Literal["High", "Medium", "Low", "Excluded"]

class DocumentProcessor:
    """Process documents for RAG."""

    def __init__(self):
        """Initialize document processor."""
        logger.info("Initializing DocumentProcessor")
        self.vector_db = VectorDBManager.get_instance()
        
        # Initialize text splitter for chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.vector_db.config.default_collection.chunk_size,
            chunk_overlap=self.vector_db.config.default_collection.chunk_overlap,
            length_function=len,
        )
        
        self._error_queue = queue.Queue()
        
        # Initialize document handlers
        self.handlers = [
            MarkItDownHandler(),  # Pour PDF, DOCX, XLSX, PPTX
            TextHandler(),        # Pour JSON, MD
            EpubHandler()         # Pour EPUB
        ]
        
        logger.info("DocumentProcessor initialization complete")

    def _process_file_internal(
        self,
        file_path: str,
        workspace_id: str,
        importance_level: ImportanceLevelType = "Medium"
    ) -> None:
        """Internal method to process a file.
        
        Args:
            file_path: Path to the file to process
            workspace_id: Workspace identifier
            importance_level: Importance level for the document
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            # Get handler for file type
            handler = next(
                (h for h in self.handlers if h.can_handle(file_path)), 
                None
            )
            if not handler:
                raise ValueError(f"No handler found for file type: {file_path.suffix}")

            # Extract text content
            logger.info(f"Extracting content from {file_path}")
            result = handler.extract_text(file_path)
            if isinstance(result, tuple):
                content, handler_metadata = result
            else:
                content = result
                handler_metadata = {}
                
            if not content:
                logger.warning(f"No content extracted from {file_path}")
                return

            # Split into chunks
            logger.info("Splitting content into chunks")
            chunks = self.text_splitter.split_text(content)
            if not chunks:
                logger.warning("No chunks created from content")
                return

            # Get file stats
            stats = file_path.stat()
            file_stats = {
                "created_at": datetime.fromtimestamp(stats.st_ctime).isoformat(),
                "modified_at": datetime.fromtimestamp(stats.st_mtime).isoformat(),
                "size_bytes": stats.st_size
            }

            # Generate unique document IDs
            file_path_hash = hashlib.sha256(str(file_path).encode()).hexdigest()[:8]
            doc_ids = [f"{workspace_id}_{file_path_hash}_{i}" for i in range(len(chunks))]

            # Prepare metadata
            base_metadata = {
                **handler_metadata,
                **file_stats,
                "source": str(file_path),
                "file_type": file_path.suffix,
                "importance_level": importance_level,
                "processed_at": datetime.now().isoformat(),
                "chunk_count": len(chunks)
            }

            # Add to vector store
            logger.info(f"Adding {len(chunks)} chunks to vector store")
            metadatas = [{**base_metadata, "chunk_index": i} for i in range(len(chunks))]
            success = self.vector_db.add_documents(
                workspace_id=workspace_id,
                texts=chunks,
                metadatas=metadatas,
                doc_ids=doc_ids
            )
            
            if success:
                logger.info(f"Successfully processed {file_path}")
            else:
                logger.error(f"Failed to add documents for {file_path}")

        except Exception as e:
            error_msg = f"Error processing {file_path}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self._error_queue.put(error_msg)

    def process_file(
        self,
        file_path: str,
        workspace_id: str,
        importance_level: ImportanceLevelType = "Medium"
    ) -> bool:
        """Process a single file.
        
        Args:
            file_path: Path to the file to process
            workspace_id: Workspace identifier
            importance_level: Importance level for the document
            
        Returns:
            True if processing was successful
        """
        try:
            self._process_file_internal(file_path, workspace_id, importance_level)
            return self._error_queue.empty()
        except Exception as e:
            logger.error(f"Error in process_file: {e}", exc_info=True)
            return False

    def get_errors(self) -> List[str]:
        """Get any errors that occurred during processing."""
        errors = []
        while not self._error_queue.empty():
            errors.append(self._error_queue.get())
        return errors

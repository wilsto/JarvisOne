"""Process and manage documents for RAG."""

import os
import logging
import queue
from datetime import datetime
from pathlib import Path
from typing import Optional, Literal, Dict, Any, List
import chromadb
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from chromadb.config import Settings

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

    def __init__(self, vector_db_path: str):
        """Initialize document processor.
        
        Args:
            vector_db_path: Base path for vector database storage
        """
        logger.info(f"Initializing DocumentProcessor with vector_db_path: {vector_db_path}")
        self.vector_db_path = Path(vector_db_path)
        
        # Initialize text splitter for chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
        logger.debug("Initializing HuggingFaceEmbeddings")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-mpnet-base-v2"
        )
        
        self._error_queue = queue.Queue()
        self._client = None
        
        # Initialize document handlers - instances créées une seule fois
        self.handlers = [
            MarkItDownHandler(),  # Pour PDF, DOCX, XLSX, PPTX
            TextHandler(),        # Pour JSON, MD
            EpubHandler()         # Pour EPUB
        ]
        
        logger.info("DocumentProcessor initialization complete")

    def _get_collection(self, workspace_id: str) -> chromadb.Collection:
        """Get or create a collection for the workspace."""
        client = self._get_chroma_client()
        collection_name = f"workspace_{workspace_id}"
        return client.get_or_create_collection(
            name=collection_name,
            metadata={"workspace": workspace_id, "hnsw:space": "cosine"}
        )

    def _get_chroma_client(self) -> chromadb.Client:
        """Get or create a ChromaDB client."""
        if self._client is None:
            logger.info("Creating new ChromaDB client")
            self.vector_db_path.mkdir(parents=True, exist_ok=True)
            
            self._client = chromadb.PersistentClient(
                path=str(self.vector_db_path)
            )
            logger.debug("ChromaDB client created successfully")
        return self._client

    def cleanup(self):
        """Clean up resources."""
        if self._client:
            logger.info("Cleaning up ChromaDB client")
            try:
                self._client.reset()
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")
            finally:
                self._client = None
                logger.debug("Client reset complete")

    def _process_file_internal(
        self,
        file_path: str,
        workspace_id: str,
        importance_level: ImportanceLevelType = "Medium"
    ) -> None:
        """Internal method to process a file."""
        try:
            path = Path(file_path)
            if not path.exists():
                logger.warning(f"File does not exist: {file_path}")
                return
                
            # Get file stats
            stats = path.stat()
            created_at = datetime.fromtimestamp(stats.st_ctime).isoformat()
            modified_at = datetime.fromtimestamp(stats.st_mtime).isoformat()
            
            # Find appropriate handler
            handler = next(
                (h for h in self.handlers if h.can_handle(path)),
                None
            )
            
            if handler is None:
                logger.warning(f"No handler found for file: {file_path}")
                return
            
            # Extract text using handler instance
            result = handler.extract_text(path)
            if isinstance(result, tuple):
                text, metadata = result
                # Merge handler metadata with our metadata
                metadatas = [{
                    **metadata,
                    "file_path": str(file_path),
                    "workspace_id": workspace_id,
                    "importance_level": importance_level,
                    "created_at": created_at,
                    "modified_at": modified_at,
                    "file_type": path.suffix.lower(),
                    "chunk_index": i
                } for i in range(len(chunks))]
            else:
                text = result
                metadatas = [{
                    "file_path": str(file_path),
                    "workspace_id": workspace_id,
                    "importance_level": importance_level,
                    "created_at": created_at,
                    "modified_at": modified_at,
                    "file_type": path.suffix.lower(),
                    "chunk_index": i
                } for i in range(len(chunks))]
                
            if not text:
                logger.warning(f"Empty file: {file_path}")
                return

            # Split text into chunks
            logger.debug("Splitting text into chunks")
            chunks = self.text_splitter.split_text(text)
            logger.info(f"Generated {len(chunks)} chunks")
            
            if not chunks:
                logger.warning(f"No chunks generated from {file_path}")
                return

            # Get collection
            collection = self._get_collection(workspace_id)
            if not collection:
                logger.error(f"Failed to get collection for workspace {workspace_id}")
                return

            # Generate embeddings and store in ChromaDB
            logger.debug("Generating embeddings")
            embeddings = self.embeddings.embed_documents(chunks)
            logger.info(f"Generated {len(embeddings)} embeddings")

            # Add documents to collection
            logger.debug("Adding documents to collection")
            collection.add(
                embeddings=embeddings,
                documents=chunks,
                metadatas=metadatas,
                ids=[f"{workspace_id}_{os.path.basename(file_path)}_{i}" for i in range(len(chunks))]
            )
            logger.info(f"Added {len(chunks)} documents to collection")

            # Verify documents were added
            count = len(collection.get()['documents'])
            logger.info(f"Collection now has {count} documents")

        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            self._error_queue.put(e)
            raise

    def process_document(
        self,
        file_path: str,
        workspace_id: str,
        importance_level: ImportanceLevelType = "Medium",
        wait_for_completion: bool = False
    ):
        """Process a document and add it to the vector store.
        
        Args:
            file_path: Path to the document to process
            workspace_id: ID of the workspace the document belongs to
            importance_level: Importance level of the document ("High", "Medium", "Low", "Excluded")
            wait_for_completion: If True, wait for processing to complete before returning
            
        Raises:
            FileNotFoundError: If the input file does not exist
            ValueError: If file is too large, unsupported type, or cannot be processed
        """
        try:
            self._process_file_internal(file_path, workspace_id, importance_level)
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            self._error_queue.put(e)
            raise

    def search_documents(
        self,
        query: str,
        workspace_id: str,
        n_results: int = 5,
        where: Dict = None
    ) -> List[Dict[str, Any]]:
        """Search for relevant documents using the query.
        
        Args:
            query: The search query
            workspace_id: ID of the workspace to search in
            n_results: Maximum number of results to return
            where: Filter conditions for the search
            
        Returns:
            List of dictionaries containing document content and metadata
        """
        try:
            # Get collection for workspace
            collection = self._get_collection(workspace_id)
            if not collection:
                logger.error(f"Failed to get collection for workspace {workspace_id}")
                return []
            
            # Generate query embedding
            logger.debug("Generating query embedding")
            query_embedding = self.embeddings.embed_query(query)
            
            # Search in collection
            logger.debug(f"Searching collection with n_results={n_results}")
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and len(results['documents'][0]) > 0:
                for doc, metadata, distance in zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
                ):
                    formatted_results.append({
                        'content': doc,
                        'metadata': metadata,
                        'similarity_score': 1 - distance  # Convert distance to similarity
                    })
                
                logger.info(f"Found {len(formatted_results)} matching documents")
                
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            self._error_queue.put(e)
            raise

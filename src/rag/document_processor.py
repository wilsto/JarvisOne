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
import hashlib

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
            model_name="sentence-transformers/all-MiniLM-L6-v2"  # 384 dimensions
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
            else:
                text = result
                metadata = {}
                
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

            # Prepare metadata for each chunk
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

            # Get collection
            collection = self._get_collection(workspace_id)
            if not collection:
                logger.error(f"Failed to get collection for workspace {workspace_id}")
                return

            # Generate embeddings and store in ChromaDB
            logger.debug("Generating embeddings")
            embeddings = self.embeddings.embed_documents(chunks)
            logger.info(f"Generated {len(embeddings)} embeddings")

            # Generate unique document IDs using full path hash
            file_path_hash = hashlib.sha256(str(file_path).encode()).hexdigest()[:8]
            doc_ids = [f"{workspace_id}_{file_path_hash}_{i}" for i in range(len(chunks))]
            
            # Check for existing documents and remove them
            try:
                # First try exact IDs
                existing_docs = collection.get(ids=doc_ids)
                if existing_docs and existing_docs['ids']:
                    logger.info(f"Found {len(existing_docs['ids'])} existing chunks for {file_path}, removing them")
                    collection.delete(ids=existing_docs['ids'])
                
                # Then check for any chunks from this file using metadata
                existing_by_path = collection.get(
                    where={"$and": [
                        {"file_path": {"$eq": str(file_path)}},
                        {"workspace_id": {"$eq": workspace_id}}
                    ]}
                )
                if existing_by_path and existing_by_path['ids']:
                    logger.info(f"Found {len(existing_by_path['ids'])} additional chunks by path, removing them")
                    collection.delete(ids=existing_by_path['ids'])
            except Exception as e:
                logger.warning(f"Error checking existing documents: {e}")

            # Add documents to collection
            logger.debug("Adding documents to collection")
            collection.add(
                embeddings=embeddings,
                documents=chunks,
                metadatas=metadatas,
                ids=doc_ids
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
            search_where = where
            if where:
                # Convert simple where dict to ChromaDB format if needed
                if not any(key.startswith('$') for key in where.keys()):
                    # If only one condition, use simple $eq
                    if len(where) == 1:
                        key, value = next(iter(where.items()))
                        search_where = {key: {"$eq": value}}
                    # If multiple conditions, use $and
                    else:
                        search_where = {
                            "$and": [{k: {"$eq": v}} for k, v in where.items()]
                        }
            
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=search_where,
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

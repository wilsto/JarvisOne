"""
Document processor module for RAG functionality in JarvisOne.
Handles text file processing, chunking, embedding generation, and vector storage.
"""

import os
import threading
import logging
from typing import Optional, Literal, Dict, Any, List
from pathlib import Path
import queue

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import SentenceTransformerEmbeddings
import chromadb
from chromadb.config import Settings

from .document_handlers import MarkItDownHandler, TextHandler, EpubHandler, BaseDocumentHandler

ImportanceLevelType = Literal["High", "Medium", "Low", "Excluded"]

# Configure logger
logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Handles document processing for RAG functionality."""
    
    def __init__(self, vector_db_path: str):
        """
        Initialize the document processor.
        
        Args:
            vector_db_path: Base path for vector database storage
        """
        logger.info(f"Initializing DocumentProcessor with vector_db_path: {vector_db_path}")
        self.vector_db_path = Path(vector_db_path)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=100,  # Smaller chunks for testing
            chunk_overlap=20,
            length_function=len,
        )
        logger.debug("Initializing SentenceTransformerEmbeddings")
        self.embeddings = SentenceTransformerEmbeddings(
            model_name="all-mpnet-base-v2"
        )
        self._error_queue = queue.Queue()
        self._client = None
        
        # Initialize document handlers
        self.handlers: List[BaseDocumentHandler] = [
            MarkItDownHandler(),  # For PDF, DOCX, XLSX, PPTX
            TextHandler(),        # For JSON, MD
            EpubHandler(),        # For EPUB
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
        importance_level: ImportanceLevelType
    ) -> None:
        """Internal method to process a text file and store in vector database."""
        try:
            # Validate file exists
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                raise FileNotFoundError(f"File not found: {file_path}")

            # Read the file
            logger.info(f"Processing file: {file_path}")
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
                logger.debug(f"Read {len(text)} characters")

            # Handle empty files
            if not text.strip():
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

            # Generate embeddings and store in ChromaDB
            logger.debug("Generating embeddings")
            embeddings = self.embeddings.embed_documents(chunks)
            logger.info(f"Generated {len(embeddings)} embeddings")

            # Prepare documents metadata
            metadatas = [{
                "file_path": file_path,
                "workspace_id": workspace_id,
                "importance_level": importance_level,
                "chunk_index": i
            } for i in range(len(chunks))]

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
        vector_db_path: str,
        importance_level: ImportanceLevelType = "Medium",
        wait_for_completion: bool = False
    ):
        """
        Process any supported document type for RAG.
        
        Args:
            file_path: Path to the document to process
            workspace_id: ID of the workspace the document belongs to
            vector_db_path: Base path for vector database storage
            importance_level: Importance level of the document ("High", "Medium", "Low", "Excluded")
            wait_for_completion: If True, wait for processing to complete before returning
            
        Raises:
            FileNotFoundError: If the input file does not exist
            ValueError: If file is too large, unsupported type, or cannot be processed
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            # Find appropriate handler
            handler = next(
                (h for h in self.handlers if h.can_handle(file_path)),
                None
            )
            
            if handler is None:
                raise ValueError(f"No handler found for file: {file_path}")

            # Extract text using appropriate handler
            text_content, metadata = handler.extract_text(file_path)
            
            # Add importance level to metadata
            metadata['importance_level'] = importance_level
            metadata['workspace_id'] = workspace_id
            
            # Process chunks
            chunks = self.text_splitter.split_text(text_content)
            
            # Get collection for workspace
            collection = self._get_collection(workspace_id)
            
            # Add chunks to collection
            for i, chunk in enumerate(chunks):
                collection.add(
                    documents=[chunk],
                    metadatas=[{**metadata, 'chunk_id': i}],
                    ids=[f"{file_path.stem}_{i}"]
                )
                
            logger.info(f"Successfully processed file: {file_path}")
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            self._error_queue.put(e)
            raise

    def search_documents(
        self,
        query: str,
        workspace_id: str,
        n_results: int = 5,
        importance_filter: Optional[ImportanceLevelType] = None,
    ) -> list[dict]:
        """
        Search for relevant documents using semantic similarity.
        
        Args:
            query: The search query
            workspace_id: ID of the workspace to search in
            n_results: Maximum number of results to return
            importance_filter: Optional filter for document importance level
            
        Returns:
            List of dictionaries containing document content and metadata
        """
        logger.info(f"Searching documents in workspace {workspace_id} with query: {query}")
        
        try:
            # Get embeddings for the query
            logger.debug("Generating query embedding")
            query_embedding = self.embeddings.embed_query(query)
            
            # Get collection
            collection = self._get_collection(workspace_id)
            
            # Prepare where clause if importance filter is specified
            where = {"importance_level": importance_filter} if importance_filter else None
            
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
            else:
                logger.info("No matching documents found")
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error during document search: {str(e)}")
            raise

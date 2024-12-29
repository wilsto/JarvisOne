"""
Document processor module for RAG functionality in JarvisOne.
Handles text file processing, chunking, embedding generation, and vector storage.
"""

import os
import threading
from typing import Optional, Literal
from pathlib import Path
import queue

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import SentenceTransformerEmbeddings
import chromadb
from chromadb.config import Settings

ImportanceLevelType = Literal["High", "Medium", "Low", "Excluded"]

class DocumentProcessor:
    """Handles document processing for RAG functionality."""
    
    def __init__(self, vector_db_path: str):
        """
        Initialize the document processor.
        
        Args:
            vector_db_path: Base path for vector database storage
        """
        self.vector_db_path = Path(vector_db_path)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=100,  # Smaller chunks for testing
            chunk_overlap=20,
            length_function=len,
        )
        self.embeddings = SentenceTransformerEmbeddings(
            model_name="all-mpnet-base-v2"
        )
        self._error_queue = queue.Queue()
        self._client = None

    def _get_workspace_db_path(self, workspace_id: str) -> Path:
        """Get the vector database path for a specific workspace."""
        return self.vector_db_path / workspace_id

    def _get_chroma_client(self, workspace_id: str) -> chromadb.Client:
        """Get or create a ChromaDB client for the workspace."""
        if self._client is None:
            db_path = self._get_workspace_db_path(workspace_id)
            db_path.mkdir(parents=True, exist_ok=True)
            
            self._client = chromadb.Client(
                Settings(
                    persist_directory=str(db_path),
                    is_persistent=True,
                    allow_reset=True  # Enable reset for cleanup
                )
            )
        return self._client

    def cleanup(self):
        """Clean up resources."""
        if self._client:
            try:
                self._client.reset()
            except Exception as e:
                print(f"Error during cleanup: {e}")
            finally:
                self._client = None

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
                raise FileNotFoundError(f"File not found: {file_path}")

            # Read the file
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
                print(f"Read {len(text)} characters from {file_path}")

            # Handle empty files
            if not text.strip():
                print(f"Empty file: {file_path}")
                db_path = self._get_workspace_db_path(workspace_id)
                db_path.mkdir(parents=True, exist_ok=True)
                return

            # Split text into chunks
            chunks = self.text_splitter.split_text(text)
            print(f"Split into {len(chunks)} chunks")
            
            if not chunks:
                print(f"No chunks generated from {file_path}")
                db_path = self._get_workspace_db_path(workspace_id)
                db_path.mkdir(parents=True, exist_ok=True)
                return

            # Setup ChromaDB
            client = self._get_chroma_client(workspace_id)
            collection = client.get_or_create_collection(
                name="documents",
                metadata={"hnsw:space": "cosine"}
            )

            # Generate embeddings and store in ChromaDB
            embeddings = self.embeddings.embed_documents(chunks)
            print(f"Generated {len(embeddings)} embeddings")

            # Prepare documents metadata
            metadatas = [{
                "file_path": file_path,
                "workspace_id": workspace_id,
                "importance_level": importance_level,
                "chunk_index": i
            } for i in range(len(chunks))]

            # Add documents to collection
            collection.add(
                embeddings=embeddings,
                documents=chunks,
                metadatas=metadatas,
                ids=[f"{workspace_id}_{os.path.basename(file_path)}_{i}" for i in range(len(chunks))]
            )
            print(f"Added {len(chunks)} documents to collection")

            # Verify documents were added
            count = len(collection.get()['documents'])
            print(f"Collection now has {count} documents")

        except Exception as e:
            print(f"Error processing file: {str(e)}")
            self._error_queue.put(e)
            raise

def process_text_file(
    file_path: str,
    workspace_id: str,
    vector_db_path: str,
    importance_level: ImportanceLevelType = "Medium",
    wait_for_completion: bool = False
) -> None:
    """
    Process a text file for RAG, including chunking, embedding generation, and storage.
    
    Args:
        file_path: Path to the text file to process
        workspace_id: ID of the workspace the document belongs to
        vector_db_path: Base path for vector database storage
        importance_level: Importance level of the document ("High", "Medium", "Low", "Excluded")
        wait_for_completion: If True, wait for processing to complete before returning
    
    This function runs asynchronously in a separate thread to avoid blocking the main thread.
    Raises:
        FileNotFoundError: If the input file does not exist
        Exception: Any other error that occurs during processing
    """
    processor = DocumentProcessor(vector_db_path)
    
    # Create and start processing thread
    process_thread = threading.Thread(
        target=processor._process_file_internal,
        args=(file_path, workspace_id, importance_level)
    )
    process_thread.start()
    
    if wait_for_completion:
        process_thread.join()
        # Check if there was an error in the thread
        try:
            error = processor._error_queue.get_nowait()
            raise error
        except queue.Empty:
            pass

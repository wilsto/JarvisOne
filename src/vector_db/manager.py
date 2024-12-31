"""Vector database manager implementation."""

import logging
from pathlib import Path
from typing import Dict, Optional, List
import chromadb
from chromadb.config import Settings
from langchain_huggingface import HuggingFaceEmbeddings

from .config import VectorDBConfig, CollectionConfig
from .monitoring import VectorDBMonitor

logger = logging.getLogger(__name__)

class VectorDBManager:
    """Centralized manager for vector database operations."""
    
    _instance = None
    
    @classmethod
    def get_instance(cls, config: dict = None) -> 'VectorDBManager':
        """Get or create the VectorDBManager singleton."""
        if cls._instance is None:
            if config is None:
                from core.config_manager import ConfigManager
                config = ConfigManager.get_all_configs()
            cls._instance = cls(config)
        return cls._instance
    
    def __init__(self, config: dict):
        """Initialize vector database manager.
        
        Args:
            config: Application configuration dictionary
        """
        logger.info("Initializing VectorDBManager")
        self.config = self._load_config(config)
        self._client = None
        self._collections: Dict[str, chromadb.Collection] = {}
        self.monitor = VectorDBMonitor()
        self.embeddings = HuggingFaceEmbeddings(
            model_name=self.config.default_collection.embedding_function,
            encode_kwargs={"normalize_embeddings": True}  # Add encoding configuration
        )
        self.initialize(self.config)
        
    def _load_config(self, config: dict) -> VectorDBConfig:
        """Load vector DB configuration from app config."""
        vector_config = config.get("vector_db", {})
        return VectorDBConfig(
            persist_directory=Path(vector_config.get("path", "data/vector_db")),
            collection_prefix=vector_config.get("collection_prefix", "workspace_"),
            default_collection=CollectionConfig(
                **vector_config.get("collection_settings", {})
            )
        )
        
    def initialize(self, config: VectorDBConfig, persist_directory: Optional[str] = None) -> None:
        """Initialize the vector database manager.
        
        Args:
            config: Vector database configuration
            persist_directory: Optional override for persist directory
        """
        self.config = config
        
        # Initialize ChromaDB client
        persist_dir = persist_directory or str(config.persist_directory)
        self._client = chromadb.PersistentClient(
            path=persist_dir,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True  # Allow reset for testing
            )
        )
        
        # Initialize monitoring
        if config.monitoring_enabled:
            self.monitor = VectorDBMonitor()
            
    @property
    def client(self) -> chromadb.Client:
        """Get or create ChromaDB client."""
        if self._client is None:
            logger.info("Creating new ChromaDB client")
            self._client = chromadb.PersistentClient(
                path=str(self.config.persist_directory),
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True  # Allow reset for testing
                )
            )
            logger.info("ChromaDB client created successfully")
        return self._client
        
    def get_collection(self, workspace_id: str, create: bool = False) -> Optional[chromadb.Collection]:
        """Get a collection for a workspace.
        
        Args:
            workspace_id: Workspace identifier
            create: If True, create collection if it doesn't exist
            
        Returns:
            ChromaDB collection or None if error
        """
        try:
            collection_name = f"{self.config.collection_prefix}{workspace_id}"
            
            if collection_name in self._collections:
                return self._collections[collection_name]
            
            try:
                # Try to get existing collection first
                collection = self.client.get_collection(name=collection_name)
            except Exception as e:
                if create:
                    # Create if requested and doesn't exist
                    collection = self.client.create_collection(
                        name=collection_name,
                        metadata={"workspace_id": workspace_id}
                    )
                else:
                    logger.error(f"Collection {collection_name} does not exist and create=False")
                    return None
                
            self._collections[collection_name] = collection
            return collection
            
        except Exception as e:
            logger.error(f"Error accessing collection {workspace_id}: {e}", exc_info=True)
            return None
            
    def add_documents(self, workspace_id: str, texts: List[str], metadatas: List[dict], doc_ids: List[str] = None) -> bool:
        """Add documents to a collection.
        
        Args:
            workspace_id: Workspace identifier
            texts: List of text content
            metadatas: List of metadata dictionaries
            doc_ids: Optional list of document IDs
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get or create collection
            collection = self.get_collection(workspace_id, create=True)
            if not collection:
                return False
                
            # Generate embeddings using correct method
            embeddings = self.embeddings.embed_documents(texts)
            
            # If doc_ids provided, check and remove existing
            if doc_ids:
                try:
                    existing_docs = collection.get(ids=doc_ids)
                    if existing_docs and existing_docs['ids']:
                        logger.info(f"Removing {len(existing_docs['ids'])} existing documents")
                        collection.delete(ids=existing_docs['ids'])
                except Exception as e:
                    logger.warning(f"Error checking existing documents: {e}")
            
            # Add to collection
            collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=doc_ids if doc_ids else [f"doc_{i}" for i in range(len(texts))]
            )
            
            # Update monitoring
            collection_name = f"{self.config.collection_prefix}{workspace_id}"
            doc_count = len(collection.get()["ids"]) if collection.get()["ids"] else 0
            self.monitor.update_collection(collection_name, doc_count)
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding documents to {workspace_id}: {e}", exc_info=True)
            return False
            
    def query(self, workspace_id: str, query_text: str, n_results: int = 3) -> List[dict]:
        """Query documents from a collection.
        
        Args:
            workspace_id: Workspace identifier
            query_text: Text to search for
            n_results: Number of results to return
            
        Returns:
            List of documents with their content and metadata
        """
        try:
            collection = self.get_collection(workspace_id)
            if not collection:
                return []
                
            # Generate query embedding using correct method
            query_embedding = self.embeddings.embed_query(query_text)
            
            # Query collection
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            # Update monitoring
            collection_name = f"{self.config.collection_prefix}{workspace_id}"
            self.monitor.record_query(collection_name)
            
            # Format results
            formatted_results = []
            if results["documents"]:
                for i, doc in enumerate(results["documents"][0]):
                    metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                    distance = results["distances"][0][i] if "distances" in results else None
                    formatted_results.append({
                        "content": doc,
                        "metadata": metadata,
                        "distance": distance
                    })
                    
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error querying {workspace_id}: {e}", exc_info=True)
            return []
            
    def get_stats(self) -> dict:
        """Get vector DB statistics."""
        return {
            "collections": len(self._collections),
            "persist_directory": str(self.config.persist_directory),
            "collection_stats": self.monitor.get_all_stats()
        }
        
    def close(self):
        """Close the ChromaDB client and cleanup resources."""
        if self._client:
            try:
                # Reset all collections
                self._collections.clear()
                # Delete the client reference
                self._client = None
                logger.info("ChromaDB client closed successfully")
            except Exception as e:
                logger.error(f"Error closing ChromaDB client: {e}", exc_info=True)

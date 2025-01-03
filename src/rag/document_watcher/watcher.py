"""File system watcher for document changes."""

import time
import logging
from pathlib import Path
from typing import List, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent, FileDeletedEvent
from datetime import datetime
import hashlib

from rag.document_processor import DocumentProcessor
from .document_tracker import DocumentTracker
from .processor import DocumentChangeProcessor

logger = logging.getLogger(__name__)

class DocumentEventHandler(FileSystemEventHandler):
    """Handles file system events for documents."""
    
    def __init__(self, workspace_id: str, doc_tracker: DocumentTracker, doc_processor: DocumentProcessor):
        """Initialize the event handler.
        
        Args:
            workspace_id: ID of the workspace
            doc_tracker: Document tracker instance
            doc_processor: Document processor instance
        """
        self.workspace_id = workspace_id
        self.doc_tracker = doc_tracker
        self.doc_processor = doc_processor
        self.supported_extensions = {
            ext for handler in doc_processor.handlers 
            for ext in handler.SUPPORTED_EXTENSIONS
        }
        logger.info(f"Initialized DocumentEventHandler for workspace {workspace_id}")
        logger.debug(f"Supported extensions: {self.supported_extensions}")

    def _should_process(self, path: Path) -> bool:
        """Check if file should be processed based on extension."""
        return path.suffix.lower() in self.supported_extensions
        
    def _get_file_info(self, file_path: Path) -> tuple:
        """Get file modification time and hash."""
        # Get modification time
        mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
        
        # Calculate file hash
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            buf = f.read(65536)  # Read in 64kb chunks
            while len(buf) > 0:
                hasher.update(buf)
                buf = f.read(65536)
        return mtime, hasher.hexdigest()
        
    def on_created(self, event: FileCreatedEvent):
        """Handle file creation event."""
        if not event.is_directory and self._should_process(Path(event.src_path)):
            path = Path(event.src_path)
            logger.info(f"New file detected: {path}")
            mtime, file_hash = self._get_file_info(path)
            self.doc_tracker.update_document(
                workspace_id=self.workspace_id,
                file_path=str(path),
                status='pending',
                last_modified=mtime,
                hash_value=file_hash
            )
            
    def on_modified(self, event: FileModifiedEvent):
        """Handle file modification event."""
        if not event.is_directory and self._should_process(Path(event.src_path)):
            path = Path(event.src_path)
            logger.info(f"File modified: {path}")
            mtime, file_hash = self._get_file_info(path)
            self.doc_tracker.update_document(
                workspace_id=self.workspace_id,
                file_path=str(path),
                status='pending',
                last_modified=mtime,
                hash_value=file_hash
            )
            
    def on_deleted(self, event: FileDeletedEvent):
        """Handle file deletion event."""
        if not event.is_directory and self._should_process(Path(event.src_path)):
            path = Path(event.src_path)
            logger.info(f"File deleted: {path}")
            
            # Get last known hash from document status
            doc_status = self.doc_tracker.get_document_status(
                workspace_id=self.workspace_id,
                file_path=str(path)
            )
            
            # Use last known hash or generate a deletion hash
            hash_value = doc_status.get('hash') if doc_status else f"deleted_{time.time()}"
            
            self.doc_tracker.update_document(
                workspace_id=self.workspace_id,
                file_path=str(path),
                status='deleted',
                hash_value=hash_value
            )

class FileSystemWatcher:
    """Watch file system for document changes."""
    
    def __init__(self, workspace_id: str, paths: List[Path], doc_tracker: DocumentTracker, doc_processor: DocumentProcessor):
        """Initialize file system watcher.
        
        Args:
            workspace_id: ID of the workspace
            paths: List of paths to watch
            doc_tracker: Document tracker instance
            doc_processor: Document processor instance
        """
        self.workspace_id = workspace_id
        self.paths = [Path(p) for p in paths]
        self.doc_tracker = doc_tracker
        self.doc_processor = doc_processor
        self.observer = Observer()
        self.processor = DocumentChangeProcessor(workspace_id, doc_processor, self.doc_tracker)
        self._setup_watchers()
        logger.info(f"Initialized FileSystemWatcher for workspace {workspace_id}")
        
    def _setup_watchers(self):
        """Set up file system observers for all paths."""
        handler = DocumentEventHandler(
            self.workspace_id,
            self.doc_tracker,
            self.doc_processor
        )
        
        for path in self.paths:
            if path.exists():
                self.observer.schedule(handler, str(path), recursive=True)
                logger.info(f"Watching directory: {path}")
            else:
                logger.warning(f"Path does not exist: {path}")

    def start(self):
        """Start watching directory."""
        logger.info(f"Starting watchers for paths: {self.paths}")
        self.observer.start()
        self.scan_existing_files()  # Scan existing files on startup
        self.processor.start()  # Start the background processor
        
    def stop(self):
        """Stop watching directory."""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
            
    def scan_existing_files(self):
        """Scan existing files in directory and update document tracker.
        
        Only updates a file to 'pending' if:
        - File is new (not in database)
        - File has changed (different hash)
        - File was previously marked as 'deleted' but exists again
        """
        handler = DocumentEventHandler(
            workspace_id=self.workspace_id,
            doc_tracker=self.doc_tracker,
            doc_processor=self.doc_processor
        )
        
        for path in self.paths:
            if not path.exists():
                logger.warning(f"Path {path} does not exist, skipping")
                continue
                
            for file_path in path.rglob('*'):
                if file_path.is_file() and handler._should_process(file_path):
                    try:
                        # Get current file info
                        mtime, current_hash = handler._get_file_info(file_path)
                        
                        # Check existing status
                        doc_status = self.doc_tracker.get_document_status(
                            workspace_id=self.workspace_id,
                            file_path=str(file_path)
                        )
                        
                        should_update = (
                            doc_status is None or  # New file
                            doc_status['status'] == 'deleted' or  # Previously deleted
                            doc_status['hash'] != current_hash  # File changed
                        )

                        logger.info(f"Should update: {should_update}, Doc status: {doc_status}")
                        
                        if should_update:
                            self.doc_tracker.update_document(
                                workspace_id=self.workspace_id,
                                file_path=str(file_path),
                                status='pending',
                                hash_value=current_hash,
                                last_modified=mtime
                            )
                    except Exception as e:
                        logger.error(f"Error processing {file_path}: {e}")
                        continue

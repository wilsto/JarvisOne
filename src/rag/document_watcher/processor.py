"""Background document processor for handling document changes."""

import time
import logging
import threading
from typing import Optional
from queue import Queue, Empty
from pathlib import Path

from rag.document_processor import DocumentProcessor
from rag.document_watcher.document_tracker import DocumentTracker
from utils.streamlit_utils import StreamlitThread

logger = logging.getLogger(__name__)

class DocumentChangeProcessor(StreamlitThread):
    """Processes document changes in background thread."""
    
    def __init__(self, workspace_id: str, doc_processor: DocumentProcessor, doc_tracker: DocumentTracker):
        """Initialize the document change processor."""
        super().__init__(daemon=True)
        self.workspace_id = workspace_id
        self.doc_processor = doc_processor
        self.doc_tracker = doc_tracker
        self._stop_event = threading.Event()
        self._processing_interval = 5  # seconds between processing batches
        logger.info(f"Initialized DocumentChangeProcessor for workspace {workspace_id}")

    def stop(self):
        """Signal the processor to stop."""
        self._stop_event.set()
        logger.info(f"Stopping processor for workspace {self.workspace_id}")

    def run(self):
        """Main processing loop."""
        logger.info(f"Starting document processor for workspace {self.workspace_id}")
        
        while not self._stop_event.is_set():
            try:
                # Get pending documents
                pending_docs = self.doc_tracker.get_pending_documents(self.workspace_id)
                
                for doc in pending_docs:
                    if self._stop_event.is_set():
                        break
                        
                    try:
                        file_path = Path(doc['file_path'])
                        current_hash = doc['hash']  # Get hash from document status
                        
                        # Skip if file no longer exists
                        if not file_path.exists():
                            logger.warning(f"File no longer exists: {file_path}")
                            self.doc_tracker.update_document(
                                workspace_id=self.workspace_id,
                                file_path=str(file_path),
                                status='deleted',
                                hash_value=current_hash,  # Keep the last known hash
                                error_message="File no longer exists"
                            )
                            continue
                            
                        # Process the document
                        logger.info(f"Processing document: {file_path}")
                        success = self.doc_processor.process_file(
                            str(file_path),
                            self.workspace_id
                        )
                        
                        if success:
                            self.doc_tracker.update_document(
                                workspace_id=self.workspace_id,
                                file_path=str(file_path),
                                status='processed',
                                hash_value=current_hash
                            )
                            logger.info(f"Successfully processed document: {file_path}")
                        else:
                            errors = self.doc_processor.get_errors()
                            error_msg = "; ".join(errors) if errors else "Unknown error"
                            self.doc_tracker.update_document(
                                workspace_id=self.workspace_id,
                                file_path=str(file_path),
                                status='error',
                                hash_value=current_hash,
                                error_message=error_msg
                            )
                            logger.error(f"Failed to process document {file_path}: {error_msg}")
                        
                    except Exception as e:
                        logger.error(f"Error processing document {doc['file_path']}: {e}")
                        self.doc_tracker.update_document(
                            workspace_id=self.workspace_id,
                            file_path=doc['file_path'],
                            status='error',
                            hash_value=doc['hash'],  # Use original hash
                            error_message=str(e)
                        )
                
                # Sleep between processing batches
                time.sleep(self._processing_interval)
                
            except Exception as e:
                logger.error(f"Error in processing loop: {e}")
                time.sleep(self._processing_interval * 2)  # Sleep longer on error

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
                        
                        # Skip if file no longer exists
                        if not file_path.exists():
                            logger.warning(f"File no longer exists: {file_path}")
                            self.doc_tracker.update_document(
                                self.workspace_id,
                                str(file_path),
                                status='deleted'
                            )
                            continue
                        
                        # Process document with workspace_id
                        self.doc_processor.process_document(
                            file_path=str(file_path),
                            workspace_id=self.workspace_id
                        )
                        self.doc_tracker.update_document(
                            self.workspace_id,
                            str(file_path),
                            status='processed'
                        )
                        logger.info(f"Successfully processed document: {file_path}")
                        
                    except Exception as e:
                        logger.error(f"Error processing document {doc['file_path']}: {e}")
                        self.doc_tracker.update_document(
                            self.workspace_id,
                            doc['file_path'],
                            status='error',
                            error_message=str(e)
                        )
                
                # Sleep between processing batches
                time.sleep(self._processing_interval)
                
            except Exception as e:
                logger.error(f"Error in processing loop: {e}")
                time.sleep(self._processing_interval * 2)  # Sleep longer on error

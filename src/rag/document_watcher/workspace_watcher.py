"""Manage document watchers for different workspaces."""

import logging
from pathlib import Path
from typing import Dict, Optional

from core.workspace_manager import WorkspaceManager, SpaceType
from rag.document_processor import DocumentProcessor
from .watcher import FileSystemWatcher
from .document_tracker import DocumentTracker

logger = logging.getLogger(__name__)

class WorkspaceWatcherManager:
    """Manages document watchers for workspaces."""
    
    def __init__(self, workspace_manager: WorkspaceManager, doc_processor: DocumentProcessor):
        """Initialize the workspace watcher manager."""
        self.workspace_manager = workspace_manager
        self.doc_processor = doc_processor
        self.doc_tracker = DocumentTracker()
        self.watchers: Dict[SpaceType, FileSystemWatcher] = {}
        logger.info("Initialized WorkspaceWatcherManager")
        
    def start_workspace_watcher(self, space_type: SpaceType) -> None:
        """Start watching a specific workspace."""
        if space_type == SpaceType.AGNOSTIC:
            logger.debug("Skipping watcher for AGNOSTIC workspace")
            return
            
        if space_type in self.watchers:
            logger.debug(f"Watcher already exists for workspace {space_type}")
            return
            
        try:
            # Get workspace paths
            space_config = self.workspace_manager.spaces.get(space_type)
            if not space_config:
                logger.warning(f"No configuration found for workspace {space_type}")
                return
                
            paths = [Path(p) for p in space_config.paths]
            if not paths:
                logger.warning(f"No paths configured for workspace {space_type}")
                return
                
            # Create and start watcher
            watcher = FileSystemWatcher(
                workspace_id=space_type.name,
                paths=paths,
                doc_tracker=self.doc_tracker,
                doc_processor=self.doc_processor
            )
            
            # Store and start watcher
            self.watchers[space_type] = watcher
            watcher.start()
            
            logger.info(f"Started watcher for workspace {space_type}")
            
        except Exception as e:
            logger.error(f"Error starting watcher for workspace {space_type}: {e}")
            raise
            
    def stop_workspace_watcher(self, space_type: SpaceType) -> None:
        """Stop watching a specific workspace."""
        if watcher := self.watchers.get(space_type):
            watcher.stop()
            del self.watchers[space_type]
            logger.info(f"Stopped watcher for workspace {space_type}")
            
    def start_coaching_workspace(self) -> None:
        """Start watching the coaching workspace."""
        self.start_workspace_watcher(SpaceType.COACHING)
        
    def stop_all_watchers(self) -> None:
        """Stop all workspace watchers."""
        for space_type, watcher in self.watchers.items():
            try:
                watcher.stop()
                logger.info(f"Stopped watcher for workspace {space_type}")
            except Exception as e:
                logger.error(f"Error stopping watcher for workspace {space_type}: {e}")
                
        self.watchers.clear()

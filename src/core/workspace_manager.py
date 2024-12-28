"""Workspace Manager for JarvisOne."""
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List, Optional
import yaml
from .prompts.generic_prompts import build_system_prompt

class SpaceType(Enum):
    """Enumeration of available workspaces."""
    PERSONAL = auto()
    COACHING = auto()
    DEV = auto()
    WORK = auto()
    AGNOSTIC = auto()

@dataclass
class SpaceConfig:
    """Configuration for a workspace."""
    name: str
    paths: List[Path]
    metadata: Dict
    search_params: Dict
    tags: List[str]
    system_prompt: Optional[str] = None

class WorkspaceManager:
    """Manages different workspaces and their configurations."""
    
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.spaces: Dict[SpaceType, SpaceConfig] = {}
        self.current_space: Optional[SpaceType] = None
        self._load_configurations()

    def _load_configurations(self) -> None:
        """Load all space configurations from YAML files."""
        spaces_dir = self.config_dir / "spaces"
        for space_type in SpaceType:
            if space_type == SpaceType.AGNOSTIC:
                # Load agnostic config file for metadata and scope
                agnostic_file = spaces_dir / "agnostic_config.yaml"
                metadata = {}
                if agnostic_file.exists():
                    with open(agnostic_file, 'r', encoding='utf-8') as f:
                        config_data = yaml.safe_load(f)
                        metadata = config_data.get('metadata', {})
                        # Load scope into metadata if present
                        if 'scope' in config_data:
                            metadata['scope'] = config_data['scope']
                
                self.spaces[space_type] = SpaceConfig(
                    name="Agnostic",
                    paths=[],
                    metadata=metadata,
                    search_params={},
                    tags=[],
                    system_prompt=config_data.get('system_prompt', None) if 'config_data' in locals() else None
                )
                continue
                
            config_file = spaces_dir / f"{space_type.name.lower()}_config.yaml"
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f)
                    metadata = config_data.get('metadata', {})
                    # Load scope into metadata if present
                    if 'scope' in config_data:
                        metadata['scope'] = config_data['scope']
                        
                    self.spaces[space_type] = SpaceConfig(
                        name=config_data['name'],
                        paths=[Path(p) for p in config_data['paths']],
                        metadata=metadata,
                        search_params=config_data.get('search_params', {}),
                        tags=config_data.get('tags', []),
                        system_prompt=config_data.get('system_prompt', None)
                    )

    def set_current_space(self, space_type: SpaceType) -> None:
        """Set the current active workspace."""
        if space_type not in self.spaces:
            raise ValueError(f"Space {space_type} not configured")
        self.current_space = space_type

    def get_current_space_config(self) -> Optional[SpaceConfig]:
        """Get the configuration for the current space."""
        if self.current_space:
            return self.spaces[self.current_space]
        return None

    def get_current_space_prompt(self) -> str:
        """Get the system prompt for the current workspace."""
        if not self.current_space:
            return None
        
        current_space_config = self.get_current_space_config()
        if not current_space_config:
            return None
            
        # Get scope from metadata
        scope = current_space_config.metadata.get('scope', '')
        
        # Get system prompt, defaulting to empty string if None
        system_prompt = current_space_config.system_prompt or ""
        
        return build_system_prompt(system_prompt, scope)

    def get_space_paths(self) -> List[Path]:
        """Get the paths for the current space."""
        if self.current_space and self.current_space in self.spaces:
            return self.spaces[self.current_space].paths
        return []

# For backward compatibility
KnowledgeSpaceManager = WorkspaceManager

"""Workspace Manager for JarvisOne."""
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List, Optional
import yaml
import os
import logging
from .prompts.generic_prompts import build_system_prompt

# Configuration du logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

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
    workspace_prompt: Optional[str] = None
    roles: List[Dict] = field(default_factory=list)

class WorkspaceManager:
    """Manages different workspaces and their configurations."""
    
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.spaces: Dict[SpaceType, SpaceConfig] = {}
        self.current_space: Optional[SpaceType] = None
        self.current_role: Optional[str] = None
        self._load_configurations()

    def _load_configurations(self) -> None:
        """Load all space configurations from YAML files."""
        spaces_dir = self.config_dir / "spaces"
        for space_type in SpaceType:
            if space_type == SpaceType.AGNOSTIC:
                # Load general config file for metadata and scope
                general_file = spaces_dir / "general_config.yaml"
                metadata = {}
                if general_file.exists():
                    with open(general_file, 'r', encoding='utf-8') as f:
                        config_data = yaml.safe_load(f)
                        metadata = config_data.get('metadata', {})
                        # Load scope into metadata if present
                        if 'scope' in config_data:
                            metadata['scope'] = config_data['scope']
                
                self.spaces[space_type] = SpaceConfig(
                    name="General",
                    paths=[],
                    metadata=metadata,
                    search_params={},
                    tags=[],
                    workspace_prompt=config_data.get('workspace_prompt', None) if 'config_data' in locals() else None
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
                        
                    # Log raw paths before expansion
                    logger.debug(f"Raw paths for {space_type}: {config_data['paths']}")
                    expanded_paths = []
                    for p in config_data['paths']:
                        expanded = os.path.expandvars(p)
                        logger.debug(f"Expanded path {p} to {expanded}")
                        if expanded == p and '$' in p:
                            logger.warning(f"Environment variable in path {p} was not expanded")
                        expanded_paths.append(Path(expanded))
                        
                    self.spaces[space_type] = SpaceConfig(
                        name=config_data['name'],
                        paths=expanded_paths,
                        metadata=metadata,
                        search_params=config_data.get('search_params', {}),
                        tags=config_data.get('tags', []),
                        workspace_prompt=config_data.get('workspace_prompt', None),
                        roles=config_data.get('roles', [])
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

    def get_current_context_prompt(self) -> str:
        """Get the combined context prompt including workspace and role context."""
        if not self.current_space:
            return ""
            
        current_space_config = self.spaces.get(self.current_space)
        if not current_space_config:
            return ""
            
        # Get base context prompt and scope
        context_prompt = current_space_config.workspace_prompt or ""
        scope = current_space_config.metadata.get('scope', "")
        
        # Add role-specific context if a role is selected
        role = next((r for r in current_space_config.roles if r['name'] == self.current_role), None)
        if role and 'prompt_context' in role:
            context_prompt = f"{context_prompt}\n\nRole Context:\n{role['prompt_context']}"
        
        return build_system_prompt(context_prompt, scope)

    def get_current_space_roles(self) -> List[Dict]:
        """Get roles for the current workspace."""
        if not self.current_space:
            return []
        current_space_config = self.spaces.get(self.current_space)
        return current_space_config.roles if current_space_config else []

    def set_current_role(self, role_name: str) -> None:
        """Set the current role."""
        if not self.current_space:
            return
        
        current_space_config = self.spaces.get(self.current_space)
        if not current_space_config or not current_space_config.roles:
            return
            
        if role_name in [role['name'] for role in current_space_config.roles]:
            self.current_role = role_name

    def get_space_paths(self) -> List[Path]:
        """Get the paths for the current space."""
        if self.current_space and self.current_space in self.spaces:
            return self.spaces[self.current_space].paths
        return []

# For backward compatibility
KnowledgeSpaceManager = WorkspaceManager

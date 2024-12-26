"""Knowledge Space Manager for JarvisOne."""
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List, Optional
import yaml

class SpaceType(Enum):
    """Enumeration of available knowledge spaces."""
    SERVIER = auto()
    PERSONAL = auto()
    COACHING = auto()
    DEV = auto()
    AGNOSTIC = auto()

@dataclass
class SpaceConfig:
    """Configuration for a knowledge space."""
    name: str
    paths: List[Path]
    metadata: Dict
    search_params: Dict
    tags: List[str]

class KnowledgeSpaceManager:
    """Manages different knowledge spaces and their configurations."""
    
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
                # Add AGNOSTIC as a special space with no paths
                self.spaces[space_type] = SpaceConfig(
                    name="Agnostic",
                    paths=[],
                    metadata={},
                    search_params={},
                    tags=[]
                )
                continue
            config_file = spaces_dir / f"{space_type.name.lower()}_config.yaml"
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f)
                    self.spaces[space_type] = SpaceConfig(
                        name=config_data['name'],
                        paths=[Path(p) for p in config_data['paths']],
                        metadata=config_data.get('metadata', {}),
                        search_params=config_data.get('search_params', {}),
                        tags=config_data.get('tags', [])
                    )

    def set_current_space(self, space_type: SpaceType) -> None:
        """Set the current active knowledge space."""
        if space_type not in self.spaces:
            raise ValueError(f"Space {space_type} not configured")
        self.current_space = space_type

    def get_current_space_config(self) -> Optional[SpaceConfig]:
        """Get the configuration for the current space."""
        if self.current_space:
            return self.spaces[self.current_space]
        return None

    def get_space_paths(self) -> List[Path]:
        """Get the paths for the current space."""
        if self.current_space and self.current_space in self.spaces:
            return self.spaces[self.current_space].paths
        return []

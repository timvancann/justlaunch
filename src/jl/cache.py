import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger


class ArgumentCache:
    """Handles persistence of recipe arguments."""

    def __init__(self, cache_dir: Optional[Path] = None):
        if cache_dir is None:
            cache_dir = Path.home() / ".cache" / "justlaunch"

        self.cache_file = cache_dir / "history.json"
        self.cache: Dict[str, Any] = {}
        self._load()

    def _load(self):
        """Loads the cache from disk."""
        if not self.cache_file.exists():
            return

        try:
            with open(self.cache_file, "r") as f:
                self.cache = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            logger.warning("Failed to load cache: {}", e)
            self.cache = {}

    def _save(self):
        """Saves the cache to disk."""
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_file, "w") as f:
                json.dump(self.cache, f, indent=2)
        except OSError as e:
            logger.warning("Failed to save cache: {}", e)

    def _get_key(self, justfile_path: str, recipe_name: str) -> str:
        """Generates a unique key for a recipe in a specific justfile."""

        abs_path = os.path.abspath(justfile_path)
        return f"{abs_path}::{recipe_name}"

    def get_last_arguments(
        self, justfile_path: str, recipe_name: str
    ) -> Dict[str, str]:
        """Retrieves the last used arguments for a recipe."""
        key = self._get_key(justfile_path, recipe_name)
        return self.cache.get(key, {})

    def save_arguments(
        self, justfile_path: str, recipe_name: str, args: Dict[str, str]
    ):
        """Saves arguments for a recipe."""
        key = self._get_key(justfile_path, recipe_name)
        self.cache[key] = args
        self._save()

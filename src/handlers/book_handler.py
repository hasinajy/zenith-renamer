from .base_handler import BaseHandler
import os
from typing import List, Dict

class BookHandler(BaseHandler):
    """Handler for renaming book files."""

    def __init__(self, args, config: Dict):
        super().__init__(args, config)

    def list_relevant_files(self, directory: str) -> List[str]:
        """List files relevant to books based on configured extensions.

        Args:
            directory (str): Directory to list files from.

        Returns:
            List[str]: List of relevant filenames.
        """
        extensions = tuple(self.config["book"]["extensions"])
        return [
            f for f in os.listdir(directory)
            if f.lower().endswith(extensions) and os.path.isfile(os.path.join(directory, f))
        ]

    def run(self) -> None:
        """Execute book renaming logic (placeholder)."""
        self.base_dir = self.args.directory
        files = self.list_relevant_files(self.base_dir)
        print(f"Book files to process: {files}")
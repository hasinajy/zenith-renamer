from .base_handler import BaseHandler
import os
from typing import List, Dict

class StdHandler(BaseHandler):
    """Handler for standard file renaming."""

    def __init__(self, args, config: Dict):
        super().__init__(args, config)
        self.creative = args.creative

    def list_relevant_files(self, directory: str) -> List[str]:
        """List all files in the specified directory.

        Args:
            directory (str): Directory to list files from.

        Returns:
            List[str]: List of all filenames.
        """
        return [
            f for f in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, f))
        ]

    def run(self) -> None:
        """Execute standard renaming logic (placeholder)."""
        self.base_dir = self.args.directory
        files = self.list_relevant_files(self.base_dir)
        print(f"Files to process: {files}")
        # Add renaming logic here
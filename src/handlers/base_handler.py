from abc import ABC, abstractmethod
import os
from typing import List, Dict, Optional

class BaseHandler(ABC):
    """Abstract base class for handling media file renaming.

    Attributes:
        args: Parsed command-line arguments.
        base_dir: The base directory of the files being processed.
    """

    def __init__(self, args, config: Dict):
        """Initialize the handler with arguments and configuration.

        Args:
            args: Parsed arguments from argparse.
            config: Configuration dictionary.
        """
        self.args = args
        self.config = config
        self.base_dir: Optional[str] = None

    def get_files(self) -> List[str]:
        """Retrieve the list of files to process and set the base directory.

        Returns:
            List[str]: List of filenames to process.
        """
        filenames = []
        if self.args.file:
            filenames = [os.path.basename(self.args.file)]
            self.base_dir = os.path.dirname(self.args.file)
        elif self.args.directory:
            try:
                filenames = self.list_relevant_files(self.args.directory)
                self.base_dir = self.args.directory
            except OSError as e:
                print(f"Error accessing directory: {e}")
        return filenames

    @abstractmethod
    def list_relevant_files(self, directory: str) -> List[str]:
        """List files relevant to the media type in the given directory.

        Args:
            directory (str): Directory to list files from.

        Returns:
            List[str]: List of relevant filenames.
        """
        pass

    @abstractmethod
    def get_renaming_map(self, filenames: List[str]) -> Dict[str, str]:
        """Generate a mapping from old filenames to new filenames.

        Args:
            filenames (List[str]): List of filenames to process.

        Returns:
            Dict[str, str]: Mapping from old names to new names.
        """
        pass

    def rename_file(self, old_name: str, new_name: str) -> None:
        """Rename a file from old_name to new_name.

        Args:
            old_name (str): Current filename.
            new_name (str): Desired new filename.
        """
        old_path = os.path.join(self.base_dir, old_name)
        new_path = os.path.join(self.base_dir, new_name)
        if old_path == new_path:
            print(f"Skipping {new_path}. Already renamed.")
        else:
            try:
                os.rename(old_path, new_path)
            except OSError as e:
                print(f"Error renaming {old_name}: {e}")

    def process_files(self) -> None:
        """Process the files by generating the renaming map and renaming them."""
        filenames = self.get_files()
        if not filenames:
            return
        renaming_map = self.get_renaming_map(filenames)
        if renaming_map:
            for old_name, new_name in renaming_map.items():
                self.rename_file(old_name, new_name)

    def run(self) -> None:
        """Orchestrate the file processing flow."""
        self.process_files()
import argparse
import os
import sys
from typing import List, Tuple


class BaseHandler:
    """
    Base class for handling file processing commands.

    Provides common functionalities like path initialization, file listing,
    and performing rename operations.
    """

    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.base_dir: str = ""
        self.target_files: List[str] = []

        if self.args.directory:
            self.base_dir = self.args.directory
        elif self.args.file:
            self.base_dir = os.path.dirname(self.args.file) or os.getcwd()
            self.target_files = [os.path.basename(self.args.file)]

    def _list_files_in_directory(
        self, directory_path: str, valid_extensions: Tuple[str, ...]
    ) -> List[str]:
        """
        Lists files within a directory that match valid extensions.
        Handles potential OS errors during listing.
        """
        try:
            return [
                filename
                for filename in os.listdir(directory_path)
                if filename.lower().endswith(valid_extensions)
            ]
        except FileNotFoundError:
            print(
                f"Error: Directory '{directory_path}' not found during file listing.",
                file=sys.stderr,
            )
            return []
        except NotADirectoryError:
            print(
                f"Error: Path '{directory_path}' is not a directory.", file=sys.stderr
            )
            return []
        except PermissionError:
            print(
                f"Error: Permission denied for directory '{directory_path}'.",
                file=sys.stderr,
            )
            return []
        except OSError as e:
            print(
                f"An OS error occurred while listing files in '{directory_path}': {e}",
                file=sys.stderr,
            )
            return []

    def _perform_rename_operation(self, old_filepath: str, new_filepath: str) -> None:
        original_basename = os.path.basename(old_filepath)
        new_basename = os.path.basename(new_filepath)

        if old_filepath == new_filepath:
            print(f"Skipped (no change): {original_basename}")
            return
        try:
            os.rename(old_filepath, new_filepath)
            print(f"Renamed: {original_basename} -> {new_basename}")
        except OSError as e:
            print(
                f"Error renaming '{original_basename}' to '{new_basename}': {e}",
                file=sys.stderr,
            )
        except Exception as e:
            print(
                f"An unexpected error occurred while renaming '{original_basename}': {e}",
                file=sys.stderr,
            )

    def handle(self) -> None:
        """Main method to process files. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement the 'handle' method.")

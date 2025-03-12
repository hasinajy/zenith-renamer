from .base_handler import BaseHandler
from utils import remove_special_characters
import os
from typing import List, Dict

class BookHandler(BaseHandler):
    BOOK_EXTENSIONS = (".pdf", ".epub", ".mobi", ".azw", ".txt")

    def list_relevant_files(self, directory: str) -> List[str]:
        """List all e-book files in the directory based on predefined extensions."""
        return [
            f for f in os.listdir(directory)
            if f.lower().endswith(self.BOOK_EXTENSIONS) and os.path.isfile(os.path.join(directory, f))
        ]

    def get_renaming_map(self, filenames: List[str]) -> Dict[str, str]:
        """Generate a renaming map by cleaning file names."""
        renaming_map = {}
        for filename in filenames:
            name, ext = os.path.splitext(filename)
            cleaned_name = remove_special_characters(name).replace(" ", "_")
            new_name = cleaned_name + ext
            renaming_map[filename] = new_name
        return renaming_map
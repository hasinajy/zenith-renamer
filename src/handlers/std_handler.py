from .base_handler import BaseHandler
from utils import remove_special_characters
import os
import uuid
from typing import List, Dict

class StdHandler(BaseHandler):
    def list_relevant_files(self, directory: str) -> List[str]:
        """List all files in the specified directory."""
        return [
            f for f in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, f))
        ]

    def get_renaming_map(self, filenames: List[str]) -> Dict[str, str]:
        """Generate a renaming map, using random names if --creative is set."""
        renaming_map = {}
        for filename in filenames:
            name, ext = os.path.splitext(filename)
            if self.args.creative:
                new_name = str(uuid.uuid4()) + ext
            else:
                cleaned_name = remove_special_characters(name).replace(" ", "_")
                new_name = cleaned_name + ext
            renaming_map[filename] = new_name
        return renaming_map
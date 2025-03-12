from .base_handler import BaseHandler
from utils import video_utils, remove_special_characters
import os
from typing import List, Dict

class MovieHandler(BaseHandler):
    def list_relevant_files(self, directory: str) -> List[str]:
        """List all video files in the specified directory using video_utils."""
        return video_utils.list_video_files(directory)

    def get_renaming_map(self, filenames: List[str]) -> Dict[str, str]:
        """Generate a renaming map by cleaning file names."""
        renaming_map = {}
        for filename in filenames:
            name, ext = os.path.splitext(filename)
            cleaned_name = remove_special_characters(name).replace(" ", "_")
            new_name = cleaned_name + ext
            renaming_map[filename] = new_name
        return renaming_map
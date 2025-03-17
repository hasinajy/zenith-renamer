from .base_handler import BaseHandler
from utils import anime_utils
import os
from typing import Dict, List, Tuple

class AnimeHandler(BaseHandler):
    """Handler for renaming anime files.

    Attributes:
        season (int): Season number provided via command line.
        online (bool): Whether to fetch data online.
    """

    def __init__(self, args, config: Dict):
        """Initialize the anime handler with arguments.

        Args:
            args: Parsed command-line arguments.
        """
        super().__init__(args, config)
        self.season = args.season
        self.online = args.online

    def list_relevant_files(self, directory: str) -> List[str]:
        """List video files relevant to anime in the given directory.

        Args:
            directory (str): Directory to list files from.

        Returns:
            List[str]: List of video filenames.
        """
        extensions = tuple(self.config["anime"]["extensions"])
        return [
            f for f in os.listdir(directory)
            if f.lower().endswith(extensions) and os.path.isfile(os.path.join(directory, f))
        ]

    def get_renaming_map(self, filenames: List[str]) -> Dict[str, str]:
        """Generate renaming map for anime files.

        Args:
            filenames (List[str]): List of filenames to process.

        Returns:
            Dict[str, str]: Mapping from old names to new names.
        """
        all_anime_info = anime_utils.get_all_anime_info(filenames, self.online)
        if len(all_anime_info) > 1 and self.season:
            print("[WARNING] The season number will be used on all anime series found.")
            user_confirmation = input("Are you sure you want to continue? (Yes/No): ")
            if user_confirmation.lower() != "yes":
                print("[INFO] Operation aborted by user.")
                return {}
        renaming_map = {}
        for series_name, series_info in all_anime_info.items():
            for season, season_info in series_info.items():
                for episode, episode_info in season_info.items():
                    old_name, new_name = self._make_new_name(episode_info, self.season)
                    renaming_map[old_name] = new_name
        return renaming_map

    def _make_new_name(self, episode_info: Tuple, season_arg: int) -> Tuple[str, str]:
        """Generate the new filename for an anime episode.

        Args:
            episode_info (Tuple): Episode information tuple (series_name, season, episode, episode_title, filename).
            season_arg (int): Season number provided via command line.

        Returns:
            Tuple[str, str]: (old_name, new_name)
        """
        series_name, season, episode, episode_title, filename = episode_info
        _, file_ext = os.path.splitext(filename)
        season_to_use = season or season_arg
        season_str = f" - S{season_to_use:02d}" if season_to_use else ""
        episode_str = f" - E{episode:02d}"
        title_str = f" - {episode_title}" if episode_title else ""
        new_name = f"{series_name}{season_str}{episode_str}{title_str}{file_ext}"
        return filename, new_name
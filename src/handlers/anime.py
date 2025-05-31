import argparse
import os
import re
import sys
from typing import Any, List, Dict, Optional, Tuple

from .base_handler import BaseHandler

SUBTITLE_EXTENSIONS: Tuple[str, ...] = (
    ".srt",
    ".vtt",
    ".ass",
    ".sub",
)
VIDEO_EXTENSIONS: Tuple[str, ...] = (".mp4", ".mkv", ".ts", ".avi")
RELEVANT_MEDIA_EXTENSIONS: Tuple[str, ...] = VIDEO_EXTENSIONS + SUBTITLE_EXTENSIONS

EPISODE_PATTERNS_CONFIG = [
    # Example: "Watch Raise wa Tanin ga Ii 1st Season Episode 01 English Subbed at Site Name"
    {
        "pattern": r"Watch\s+(?P<series_name>.*?) (?P<season_num>\d+)(?:st|nd|rd|th)? Season Episode\s+(?P<episode_num>\d+)",
        "groups": {
            "series_name": "series_name",
            "season_num": "season_num",
            "episode_num": "episode_num",
        },
        "season_default": None,
    },
    # Example: "Raise wa Tanin ga Ii 1st Season Episode 01 English Subbed at Site Name"
    {
        "pattern": r"^(?P<series_name>.*?) (?P<season_num>\d+)(?:st|nd|rd|th)? Season Episode\s+(?P<episode_num>\d+)",
        "groups": {
            "series_name": "series_name",
            "season_num": "season_num",
            "episode_num": "episode_num",
        },
        "season_default": None,
    },
    # Example: "Watch Raise wa Tanin ga Ii Episode 01 English Subbed at Site Name"
    {
        "pattern": r"Watch\s+(?P<series_name>.*?) Episode\s+(?P<episode_num>\d+)",
        "groups": {"series_name": "series_name", "episode_num": "episode_num"},
        "season_default": None,
    },
    # Example: "Raise wa Tanin ga Ii Episode 01 English Subbed at Site Name"
    {
        "pattern": r"^(?P<series_name>.*?) Episode\s+(?P<episode_num>\d+)",
        "groups": {"series_name": "series_name", "episode_num": "episode_num"},
        "season_default": None,
    },
]


class AnimeHandler(BaseHandler):
    """
    Handles the renaming of anime files.
    """

    def __init__(self, args: argparse.Namespace):
        super().__init__(args)
        self.episode_patterns_config = EPISODE_PATTERNS_CONFIG
        self.relevant_media_extensions = RELEVANT_MEDIA_EXTENSIONS

    def _process_match(
        self, config: Dict[str, Any], match: re.Match, file_ext: str
    ) -> Tuple[Optional[str], Optional[int], Optional[int], str]:
        """
        Processes a regex match object based on its associated configuration.

        Args:
            config: Pattern configuration.
            match: A re.Match object.
            file_ext: The file extension.

        Returns:
            Tuple of (series_name, season_num, episode_num, file_ext).
        """
        series_name = (
            match.group(config["groups"].get("series_name")).strip()
            if "series_name" in config["groups"]
            else None
        )

        season_num = None
        if "season_num" in config["groups"]:
            try:
                season_num = int(match.group(config["groups"]["season_num"]))
            except (ValueError, IndexError):
                season_num = None
        elif "season_default" in config:
            season_num = config.get("season_default")

        episode_num = None
        if "episode_num" in config["groups"]:
            try:
                episode_num = int(match.group(config["groups"]["episode_num"]))
            except (ValueError, IndexError):
                episode_num = None

        return (series_name, season_num, episode_num, file_ext)

    def _extract_anime_info(
        self, filename: str
    ) -> Tuple[Optional[str], Optional[int], Optional[int], str]:
        """
        Matches a filename against predefined patterns to extract anime info.

        Args:
            filename: The name of the file.

        Returns:
            Tuple of (series_name, season_num, episode_num, file_ext).
            Returns (None, None, None, file_ext) if no pattern matches.
        """
        _, file_ext = os.path.splitext(filename)
        for config_item in self.episode_patterns_config:
            compiled_pattern = re.compile(config_item["pattern"], re.IGNORECASE)
            match = compiled_pattern.search(filename)
            if match:
                return self._process_match(config_item, match, file_ext=file_ext)
        return (None, None, None, file_ext)

    def _construct_new_anime_filename(
        self,
        series_name: str,
        episode_num: int,
        file_ext: str,
        season: Optional[int] = None,
        episode_title: Optional[str] = None,
    ) -> str:
        """
        Constructs the new standardized filename for an anime episode.

        Args:
            series_name: Name of the anime series.
            episode_num: Episode number.
            file_ext: File extension.
            season: Season number (optional).
            episode_title: Episode title (optional).

        Returns:
            The new standardized filename.
        """
        season_str = f"S{season:02d}" if season is not None and season != 0 else None
        episode_num_str = f"E{episode_num:02d}"

        name_parts = [series_name.strip()]  # Ensure series name is stripped
        if season_str:
            name_parts.append(season_str)
        name_parts.append(episode_num_str)
        if episode_title:
            sanitized_title = re.sub(r'[<>:"/\\|?*]', "", episode_title.strip())
            if sanitized_title:
                name_parts.append(sanitized_title)

        return " - ".join(name_parts) + file_ext

    def _rename_anime_file(
        self,
        current_filepath: str,
        original_filename: str,
        season_override: Optional[int] = None,
        episode_title: Optional[str] = None,
    ) -> None:
        """
        Renames a single anime file based on extracted info and provided details.

        Args:
            current_filepath: Full current path to the file.
            original_filename: Original filename (basename).
            season_override: Season number to use in the new filename.
            episode_title: Optional episode title.
        """
        try:
            series_name, _, episode_num, file_ext = self._extract_anime_info(
                original_filename
            )

            if (
                series_name and episode_num is not None and file_ext is not None
            ):  # file_ext can be ""
                new_name = self._construct_new_anime_filename(
                    series_name=series_name,
                    episode_num=episode_num,
                    file_ext=file_ext,
                    season=season_override,
                    episode_title=episode_title,
                )
                new_filepath = os.path.join(os.path.dirname(current_filepath), new_name)
                super()._perform_rename_operation(current_filepath, new_filepath)
            else:
                print(
                    f"Skipping: {original_filename} (could not extract essential info for renaming)"
                )
        except Exception as e:
            print(
                f"An unexpected error occurred while preparing to rename '{original_filename}': {e}",
                file=sys.stderr,
            )

    def _process_anime_files(
        self,
        files_to_process: List[str],
        default_season_from_args: int,
        episode_data: Optional[Dict[Tuple[str, int, int], str]] = None,
    ):
        """
        Processes a list of anime files, attempting to rename them.

        Args:
            files_to_process: List of filenames (basenames) to process.
            default_season_from_args: Default season number from CLI args.
            episode_data: Optional dictionary of episode titles.
        """
        for original_filename in files_to_process:
            current_filepath = os.path.join(self.base_dir, original_filename)

            series_name, season_from_file, episode_num, _ = self._extract_anime_info(
                original_filename
            )

            effective_season = (
                season_from_file
                if season_from_file is not None
                else default_season_from_args
            )

            episode_title = None
            if series_name and episode_num is not None and episode_data:
                episode_title = episode_data.get(
                    (series_name, effective_season, episode_num)
                )

            self._rename_anime_file(
                current_filepath,
                original_filename,
                season_override=effective_season,
                episode_title=episode_title,
            )

    def handle(self) -> None:
        """
        Main method to handle the anime renaming process.
        Orchestrates file listing, info extraction, and renaming.
        """
        print("Processing anime files...")
        print(f"Online mode: {self.args.online}")

        if not self.target_files and self.args.directory:
            self.target_files = super()._list_files_in_directory(
                self.args.directory, self.relevant_media_extensions
            )
            if not self.target_files:
                print(
                    f"No relevant anime files found in directory '{self.args.directory}'."
                )
                return

        if not self.target_files:
            print("No files to process for anime command.", file=sys.stderr)
            return

        episode_data: Optional[Dict[Tuple[str, int, int], str]] = None
        if self.args.online:
            # TODO: Implement online data fetching logic
            pass

        self._process_anime_files(
            self.target_files,
            default_season_from_args=self.args.season,
            episode_data=episode_data,
        )

import argparse
import os
import json
import csv
import re
import sys
from typing import Any, List, Dict, Optional, Tuple

from .base_handler import BaseHandler

try:
    from .jikan_client import JikanFetcher, sanitize_filename
except ImportError:
    JikanFetcher = None  # type: ignore
    sanitize_filename = None  # type: ignore


SUBTITLE_EXTENSIONS: Tuple[str, ...] = (
    ".srt",
    ".vtt",
    ".ass",
    ".sub",
)
VIDEO_EXTENSIONS: Tuple[str, ...] = (
    ".mp4",
    ".mkv",
    ".ts",
    ".avi",
)  # Default video extensions

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
        # Initialize with default configurations
        self.subtitle_extensions: Tuple[str, ...] = SUBTITLE_EXTENSIONS
        self.video_extensions: Tuple[str, ...] = VIDEO_EXTENSIONS
        self.episode_patterns_config: List[Dict[str, Any]] = list(
            EPISODE_PATTERNS_CONFIG
        )  # Use a copy

        # Load external config if provided by the user
        if hasattr(args, "config") and args.config:
            self._load_external_config(args.config)

        # Combine extensions to determine relevant media files
        self.relevant_media_extensions: Tuple[str, ...] = (
            self.video_extensions + self.subtitle_extensions
        )

    # ----------------------- Configuration Loading Methods ---------------------- #
    def _set_video_extensions(self, extensions_value: Any, config_path: str) -> None:
        """
        Sets video extensions from a configuration value.

        Args:
            extensions_value: The value from the configuration file.
            config_path: Path to the JSON configuration file (for logging).
        """
        if isinstance(extensions_value, list) and all(
            isinstance(ext, str) for ext in extensions_value
        ):
            self.video_extensions = tuple(extensions_value)
            print(f"  Loaded custom video extensions: {self.video_extensions}")
        else:
            print(
                f"  Warning: 'video_extensions' in '{config_path}' is not a list of strings. Using defaults.",
                file=sys.stderr,
            )

    def _set_subtitle_extensions(self, extensions_value: Any, config_path: str) -> None:
        """
        Sets subtitle extensions from a configuration value.

        Args:
            extensions_value: The value from the configuration file.
            config_path: Path to the JSON configuration file (for logging).
        """
        if isinstance(extensions_value, list) and all(
            isinstance(ext, str) for ext in extensions_value
        ):
            self.subtitle_extensions = tuple(extensions_value)
            print(f"  Loaded custom subtitle extensions: {self.subtitle_extensions}")
        else:
            print(
                f"  Warning: 'subtitle_extensions' in '{config_path}' is not a list of strings. Using defaults.",
                file=sys.stderr,
            )

    def _set_episode_patterns(self, patterns_value: Any, config_path: str) -> None:
        """
        Sets episode patterns from a configuration value.

        Args:
            patterns_value: The value from the configuration file.
            config_path: Path to the JSON configuration file (for logging).
        """
        if isinstance(patterns_value, list):
            self.episode_patterns_config = patterns_value
            print(
                f"  Loaded {len(self.episode_patterns_config)} custom episode patterns."
            )
        else:
            print(
                f"  Warning: 'episode_patterns' in '{config_path}' is not a list. Using defaults.",
                file=sys.stderr,
            )

    def _load_external_config(self, config_path: str) -> None:
        """
        Loads configuration from a JSON file.
        Overrides default extensions and patterns if specified in the config.

        Args:
            config_path: Path to the JSON configuration file.
        """
        try:
            with open(config_path, "r") as f:
                config_data = json.load(f)
            print(f"Successfully loaded configuration from '{config_path}'.")

            if "video_extensions" in config_data:
                self._set_video_extensions(config_data["video_extensions"], config_path)

            if "subtitle_extensions" in config_data:
                self._set_subtitle_extensions(
                    config_data["subtitle_extensions"], config_path
                )

            if "episode_patterns" in config_data:
                self._set_episode_patterns(config_data["episode_patterns"], config_path)

        except FileNotFoundError:
            print(
                f"Warning: Configuration file '{config_path}' not found. Using default configurations.",
                file=sys.stderr,
            )
        except json.JSONDecodeError:
            print(
                f"Warning: Error decoding JSON from '{config_path}'. Using default configurations.",
                file=sys.stderr,
            )
        except Exception as e:
            print(
                f"Warning: An unexpected error occurred while loading configuration from '{config_path}': {e}. Using default configurations.",
                file=sys.stderr,
            )

    # ------------- Anime Information Extraction and Renaming Methods ------------ #
    def _process_match(
        self, config: Dict[str, Any], match: re.Match, file_ext: str
    ) -> Tuple[Optional[str], Optional[int], Optional[int], str]:
        """
        Processes a regex match object based on its associated configuration.

        Args:
            config: The specific pattern configuration dictionary from
                    `EPISODE_PATTERNS_CONFIG` (or custom loaded patterns)
                    that yielded the match.
            match: The `re.Match` object resulting from a successful pattern search.
            file_ext: The file extension of the processed file (e.g., ".mkv").

        Returns:
            A tuple containing: (series_name, season_num, episode_num, file_ext).
            Each of series_name, season_num, episode_num can be None if not found.
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
            A tuple containing: (series_name, season_num, episode_num, file_ext).
            Series name, season number, or episode number will be None if not found.
            Returns (None, None, None, file_ext) if no configured pattern matches.
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
            season: Optional season number. If 0 or None, it's omitted from the filename.
            episode_title: Optional episode title. Invalid filename characters
                            (e.g., <, >, :, ", /, \\, |, ?, *) will be removed.

        Returns:
            The new standardized filename.
        """
        season_str = (
            f"S{season:02d}" if season is not None and season != 0 else None
        )  # Season 0 is often treated as not having a season prefix
        episode_num_str = f"E{episode_num:02d}"

        name_parts = [series_name.strip()]  # Ensure series name is stripped
        if season_str:
            name_parts.append(season_str)
        name_parts.append(episode_num_str)
        if episode_title:
            # Sanitize episode title by removing characters invalid in filenames
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
        series_title_override: Optional[str] = None,
    ) -> None:
        """
        Renames a single anime file based on extracted info and provided details.

        Args:
            current_filepath: Full current path to the file.
            original_filename: Original filename (basename).
            season_override: Effective season number to use in the new filename.
            episode_title: Optional episode title for the new filename.
            series_title_override: Optional series title to use, overriding any
                                   extracted series title from the filename.
        """
        try:
            extracted_series_name, _, episode_num, file_ext = self._extract_anime_info(
                original_filename
            )

            # Determine the final series name: override if provided, else extracted.
            final_series_name = (
                series_title_override
                if series_title_override
                else extracted_series_name
            )

            if (
                final_series_name and episode_num is not None and file_ext is not None
            ):  # file_ext can be ""
                new_name = self._construct_new_anime_filename(
                    series_name=final_series_name,
                    episode_num=episode_num,
                    file_ext=file_ext,
                    season=season_override,
                    episode_title=episode_title,
                )
                new_filepath = os.path.join(os.path.dirname(current_filepath), new_name)
                super()._perform_rename_operation(current_filepath, new_filepath)
            else:
                missing_parts = []
                if not final_series_name:
                    missing_parts.append("series name")
                if episode_num is None:
                    missing_parts.append("episode number")
                print(
                    f"Skipping: {original_filename} (could not determine {', '.join(missing_parts)} for renaming)"
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
        series_title_override: Optional[str] = None,
        episode_data: Optional[Dict[int, str]] = None,
    ):
        """
        Processes a list of anime files, attempting to rename them.

        Args:
            files_to_process: List of filenames (basenames) to process.
            default_season_from_args: Default season number from CLI args, used if
                                      season cannot be extracted from filename.
            series_title_override: Optional series title to use for all files.
            episode_data: Optional dictionary mapping episode number to episode title.
        """
        for original_filename in files_to_process:
            current_filepath = os.path.join(self.base_dir, original_filename)

            _series_name_from_file, season_from_file, episode_num, _ = (
                self._extract_anime_info(original_filename)
            )

            effective_season = (
                season_from_file
                if season_from_file is not None
                else default_season_from_args
            )

            episode_title = None
            if episode_num is not None and episode_data:
                episode_title = episode_data.get(episode_num)

            self._rename_anime_file(
                current_filepath,
                original_filename,
                season_override=effective_season,
                episode_title=episode_title,
                series_title_override=series_title_override,
            )

    # -------------------- Jikan API and CSV Handling Methods -------------------- #
    def _load_episode_titles_from_csv(
        self, csv_filepath: str
    ) -> Optional[Dict[int, str]]:
        """
        Loads episode titles from a Jikan-generated CSV file.
        The CSV is expected to have 'Episode MAL ID' and 'Episode Title' columns.

        Args:
            csv_filepath: Path to the CSV file.

        Returns:
            A dictionary mapping episode number (integer, from 'Episode MAL ID')
            to episode title (string), or None if the file cannot be read,
            is improperly formatted, or contains no valid entries.
        """
        episode_titles: Dict[int, str] = {}
        try:
            with open(csv_filepath, "r", newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                if (
                    "Episode MAL ID" not in reader.fieldnames
                    or "Episode Title" not in reader.fieldnames
                ):
                    print(
                        f"Error: CSV file '{csv_filepath}' is missing required columns ('Episode MAL ID', 'Episode Title').",
                        file=sys.stderr,
                    )
                    return None

                for i, row in enumerate(reader):
                    try:
                        episode_mal_id_str = row.get("Episode MAL ID")
                        episode_title = row.get("Episode Title")

                        if episode_mal_id_str is None or episode_title is None:
                            print(
                                f"Warning: Skipping row {i+2} in '{csv_filepath}' due to missing MAL ID or Title.",
                                file=sys.stderr,
                            )
                            continue

                        episode_num = int(episode_mal_id_str)
                        episode_titles[episode_num] = episode_title
                    except ValueError:
                        print(
                            f"Warning: Invalid episode number '{row.get('Episode MAL ID')}' in '{csv_filepath}' at row {i+2}. Skipping.",
                            file=sys.stderr,
                        )
                        continue
            return episode_titles if episode_titles else None
        except FileNotFoundError:
            # This case should ideally be caught before calling this function, but good to have.
            print(f"Error: CSV file '{csv_filepath}' not found.", file=sys.stderr)
            return None
        except (csv.Error, IOError) as e:
            print(
                f"Error reading or parsing CSV file '{csv_filepath}': {e}",
                file=sys.stderr,
            )
            return None

    def _determine_series_title_for_jikan(self) -> Optional[str]:
        """
        Determines the series title to be used for Jikan search and as an override for renaming.
        Priority: --title CLI arg, then inferred from filenames if --online is active.

        Returns:
            The series title string if specified or successfully inferred, otherwise None.
        """
        if hasattr(self.args, "title") and self.args.title:
            return self.args.title

        if self.args.online and self.target_files:
            print(
                "No --title provided for online search, attempting to infer from filenames..."
            )
            for filename in self.target_files:
                extracted_name, _, _, _ = self._extract_anime_info(filename)
                if extracted_name:
                    print(
                        f"Using inferred series title '{extracted_name}' for Jikan search. For best results, provide --title."
                    )
                    return extracted_name
        return None

    def _fetch_online_data_if_needed(
        self, series_title_for_jikan: Optional[str]
    ) -> None:
        """
        Fetches anime data (ID and episodes) from Jikan API and saves it to a CSV.
        This occurs if online mode is enabled and a series title is available.

        Args:
            series_title_for_jikan: The series title to use for the Jikan API search.
        """
        if not self.args.online or not series_title_for_jikan:
            if self.args.online and not series_title_for_jikan:
                print(
                    "Skipping online data fetching: No series title specified via --title and could not infer from filenames."
                )
            return

        print("Online mode enabled: Attempting to fetch data from Jikan API...")
        if JikanFetcher is None:
            print(
                "Error: JikanFetcher is not available. Cannot perform online fetch. Is jikanpy-v4 installed?",
                file=sys.stderr,
            )
            return

        try:
            fetcher = JikanFetcher()
            csv_file_path = fetcher.fetch_and_save_anime_data_to_csv(
                series_title_for_jikan, self.base_dir
            )
            if csv_file_path:
                print(
                    f"Jikan API data for '{series_title_for_jikan}' saved to: {csv_file_path}"
                )
            else:
                print(
                    f"Failed to fetch or save anime data for '{series_title_for_jikan}' from Jikan API."
                )
        except ImportError:
            print(
                "Error: Jikan library import failed. Cannot use --online features.",
                file=sys.stderr,
            )

    def _load_episode_data_from_csv_if_available(
        self, series_title_for_csv: Optional[str]
    ) -> Optional[Dict[int, str]]:
        """
        Loads episode titles from a Jikan-generated CSV file if it exists.
        The CSV filename is expected to be based on the sanitized series title.

        Args:
            series_title_for_csv: The series title used to locate the corresponding CSV.

        Returns:
            A dictionary mapping episode number (int) to episode title (str) if the CSV
            is found and successfully parsed, otherwise None.
        """
        if not series_title_for_csv or sanitize_filename is None:
            if (
                series_title_for_csv and sanitize_filename is None
            ):  # only print warning if title was there but util is not
                print(
                    "Warning: sanitize_filename utility not available (jikan_client import issue?). Cannot reliably locate Jikan CSV for episode titles.",
                    file=sys.stderr,
                )
            return None

        sanitized_title_for_csv = sanitize_filename(series_title_for_csv)
        csv_filename = f"{sanitized_title_for_csv}_episodes_jikan.csv"
        csv_filepath = os.path.join(self.base_dir, csv_filename)

        if os.path.exists(csv_filepath):
            print(f"Attempting to load episode titles from '{csv_filepath}'...")
            loaded_data = self._load_episode_titles_from_csv(csv_filepath)
            if loaded_data:
                print(
                    f"Successfully loaded {len(loaded_data)} episode titles from CSV for renaming."
                )
            else:
                print(
                    f"Could not load episode titles from '{csv_filepath}' or CSV was empty/invalid."
                )
            return loaded_data
        else:
            print(
                f"Jikan data CSV '{csv_filepath}' not found. Proceeding without episode titles from CSV."
            )
        return None

    # ---------------------------- Main Handling Logic --------------------------- #
    def _initialize_target_files(self) -> bool:
        """Initializes target files if not already set and a directory is provided.

        Returns:
            True if target files are set (either from a single file argument or by
            finding relevant files in a directory), or if files were already initialized.
            False if a directory was provided but no relevant files were found.
        """
        if (
            not self.target_files and self.args.directory
        ):  # Only list if directory is given and files not set by --file
            self.target_files = super()._list_files_in_directory(
                self.args.directory, self.relevant_media_extensions
            )
            if not self.target_files:
                print(
                    f"No relevant anime files found in directory '{self.args.directory}'."
                )
                return False
        return True

    def handle(self) -> None:
        """
        Main method to handle the anime renaming process.
        Orchestrates file listing, info extraction, and renaming.
        """
        print("Processing anime files...")
        print(f"Online mode: {self.args.online}")

        if not self._initialize_target_files():
            return  # No files to process

        if not self.target_files:
            print("No files to process for anime command.", file=sys.stderr)
            return

        series_title_for_processing = self._determine_series_title_for_jikan()

        self._fetch_online_data_if_needed(series_title_for_processing)

        loaded_episode_data = self._load_episode_data_from_csv_if_available(
            series_title_for_processing
        )

        self._process_anime_files(
            self.target_files,
            default_season_from_args=self.args.season,
            series_title_override=series_title_for_processing,
            episode_data=loaded_episode_data,
        )

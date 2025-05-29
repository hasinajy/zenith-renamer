import argparse
import os
import re
from typing import Any, List, Dict, Optional, Tuple

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


def _process_match(
    config: Dict[str, Any], match: re.Match, file_ext: Optional[str] = None
) -> Tuple[Optional[str], Optional[int], Optional[int], Optional[str]]:
    """
    Processes a regex match object based on its associated configuration and returns extracted data.

    This function uses named capture groups from the regex pattern defined in the config
    to extract the series name, season number, and episode number in a robust way,
    independent of the order of capture groups.

    Args:
        config: A dictionary containing the pattern configuration, including
                the 'groups' mapping and 'season_default' (if applicable).
        match: A re.Match object resulting from a successful regex search.
        file_ext: The file extension (e.g., ".mkv", ".mp4").

    Returns:
        A tuple containing:
        - series_name (str or None): The extracted series name.
        - season_num (int or None): The extracted season number, or None if not present/defaulted.
        - episode_num (int or None): The extracted episode number.
        - file_ext (str or None): The original file extension.
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
        season_num = config["season_default"]

    episode_num = None
    if "episode_num" in config["groups"]:
        try:
            episode_num = int(match.group(config["groups"]["episode_num"]))
        except (ValueError, IndexError):
            episode_num = None

    return (series_name, season_num, episode_num, file_ext)


def _extract_anime_info(
    filename: str, patterns_config: List[Dict[str, Any]] = EPISODE_PATTERNS_CONFIG
) -> Tuple[Optional[str], Optional[int], Optional[int], Optional[str]]:
    """
    Matches a filename against a list of predefined patterns to extract anime information.

    It iterates through the `patterns_config`, attempting to find a match.
    The first successful match's data is processed and returned.

    Args:
        filename: The full name of the file (e.g., "My Anime - S01E05.mkv").
        patterns_config: A list of dictionaries, where each dictionary defines a regex
                         pattern and how to process its capture groups. Defaults to
                         `EPISODE_PATTERNS_CONFIG`.

    Returns:
        A tuple containing:
        - series_name (str or None): The extracted series name.
        - season_num (int or None): The extracted season number.
        - episode_num (int or None): The extracted episode number.
        - file_ext (str or None): The original file extension (e.g., ".mkv").
        Returns (None, None, None, None) if no pattern matches.
    """
    file_ext = os.path.splitext(filename)[1]
    for config in patterns_config:
        compiled_pattern = re.compile(config["pattern"], re.IGNORECASE)
        match = compiled_pattern.search(filename)
        if match:
            return _process_match(config, match, file_ext=file_ext)

    return (None, None, None, None)


def _list_anime_files(
    directory_path: str, valid_extensions: Tuple[str, ...] = RELEVANT_MEDIA_EXTENSIONS
) -> List[str]:
    """
    Lists files within a specified directory that match a given set of valid extensions.

    This function iterates through all entries in the provided directory and returns
    a list of filenames (not full paths) that have one of the specified extensions.
    The extension check is case-insensitive.

    Args:
        directory_path: The path to the directory to scan for media files.
        valid_extensions: A tuple of string extensions (e.g., ".mp4", ".srt")
                          to filter the files by. Defaults to RELEVANT_MEDIA_EXTENSIONS.

    Returns:
        A list of strings, where each string is the basename of a file that
        matches the criteria.

    Raises:
        FileNotFoundError: If the specified `directory_path` does not exist.
        NotADirectoryError: If the specified `directory_path` exists but is not a directory.
        PermissionError: If the user does not have sufficient permissions to access the directory.
    """
    return [
        filename
        for filename in os.listdir(directory_path)
        if filename.lower().endswith(valid_extensions)
    ]


def _construct_new_anime_filename(
    series_name: str,
    episode_num: int,
    file_ext: str,
    season: Optional[int] = None,
    episode_title: Optional[str] = None,
) -> str:
    """
    Constructs the new standardized filename for an anime episode.

    Args:
        series_name: The name of the anime series.
        episode_num: The episode number.
        file_ext: The file extension (e.g., ".mkv").
        season: The season number. If None or 0, it's not included in the filename.
        episode_title: The title of the episode (optional).

    Returns:
        A string representing the new standardized filename.
    """
    season_str = f"S{season:02d}" if season is not None and season != 0 else None
    episode_num_str = f"E{episode_num:02d}"

    name_parts = [series_name]
    if season_str:
        name_parts.append(season_str)
    name_parts.append(episode_num_str)
    if episode_title:
        name_parts.append(episode_title)

    return " - ".join(name_parts) + file_ext


def _perform_rename_operation(
    old_path: str, new_path: str, original_filename: str
) -> None:
    """
    Executes the file renaming operation and reports its status.

    Args:
        old_path: The current full path of the file.
        new_path: The desired full path for the renamed file.
        original_filename: The original basename of the file, used for logging.

    Side Effects:
        Renames the file on the filesystem if paths are different.
        Prints messages to stdout.
    """
    if old_path != new_path:
        os.rename(old_path, new_path)
        print(f"Renamed: {original_filename} -> {os.path.basename(new_path)}")
    else:
        print(
            f"Did not rename: {os.path.basename(new_path)} (new path is same as old path)"
        )


def _rename_anime_file(
    old_path: str,
    filename: str,
    season: Optional[int] = None,
    episode_title: Optional[str] = None,
) -> None:
    """
    Renames a single anime file based on extracted information and provided details.

    This function orchestrates the process of extracting information, constructing
    the new filename, and performing the actual file system rename.

    Args:
        old_path: The full current path to the file.
        filename: The original filename (basename) without the directory.
        season: The season number to include in the new filename (e.g., 1 for S01).
                If None or 0, season will not be included unless explicitly required.
        episode_title: An optional title for the episode, fetched from an API.

    Side Effects:
        May rename a file on the filesystem.
        Prints status messages and error messages to stdout/stderr.
    """
    series_name, _, episode_num, file_ext = _extract_anime_info(filename)
    try:
        if series_name and episode_num is not None and file_ext:
            new_name = _construct_new_anime_filename(
                series_name=series_name,
                episode_num=episode_num,
                file_ext=file_ext,
                season=season,
                episode_title=episode_title,
            )
            new_path = os.path.join(os.path.dirname(old_path), new_name)
            _perform_rename_operation(old_path, new_path, filename)
        else:
            print(
                f"Skipping: {filename} (could not extract essential info for renaming)"
            )
    except OSError as e:
        print(f"Error renaming '{filename}': {e}", file=os.sys.stderr)
    except Exception as e:
        print(
            f"An unexpected error occurred while processing '{filename}': {e}",
            file=os.sys.stderr,
        )


def _process_filenames(
    filenames: List[str],
    base_dir: str,
    default_season: int = 0,
    episode_data: Optional[Dict[Tuple[str, int, int], str]] = None,
):
    """
    Processes a list of files, attempting to rename them based on extracted info
    and optional online episode data.

    Args:
        files: A list of filenames (basenames) to process.
        base_dir: The base directory where the files are located.
        default_season: A default season number to use if one cannot be extracted
                        from the filename. Defaults to 0 (no season).
        episode_data: A dictionary containing episode titles, where keys are
                      (series_name, season_num, episode_num) tuples.
                      Defaults to None if no online data is available.

    Side Effects:
        Initiates file renaming operations.
        Prints status messages to stdout.
    """
    for filename in filenames:
        old_path = os.path.join(base_dir, filename) if base_dir else filename

        # Extract existing info from the filename first
        series_name, season_from_file, episode_num, _ = _extract_anime_info(filename)

        # Determine the effective season for this file:
        # Prefer season from file, otherwise use the default_season provided.
        effective_season = (
            season_from_file if season_from_file is not None else default_season
        )

        episode_title = None
        if series_name and episode_num is not None and episode_data:
            # Use the effective_season when looking up episode data
            episode_title = episode_data.get(
                (series_name, effective_season, episode_num)
            )

        _rename_anime_file(
            old_path, filename, season=effective_season, episode_title=episode_title
        )


def handle_anime(args: argparse.Namespace):
    """
    Handles the 'anime' command for ZenithRenamer, processing anime files.

    This function orchestrates the process of identifying files, optionally
    fetching online episode data, and then renaming the files.

    Args:
        args: The argparse.Namespace object containing parsed command-line
              arguments, specifically `directory`, `file`, `season`, and `online`.

    Side Effects:
        Prints processing information and errors to stdout/stderr.
        Triggers file renaming operations.
    """
    print("Processing anime files...")
    print(f"Online mode: {args.online}")

    base_dir = ""
    filenames: List[str] = []

    if args.directory:
        try:
            filenames = _list_anime_files(args.directory)
            base_dir = args.directory
        except FileNotFoundError:
            print(
                f"Error: The specified directory '{args.directory}' does not exist.",
                file=os.sys.stderr,
            )
            return
        except NotADirectoryError:
            print(
                f"Error: The path '{args.directory}' exists but is not a directory.",
                file=os.sys.stderr,
            )
            return
        except PermissionError:
            print(
                f"Error: Permission denied when accessing directory '{args.directory}'. "
                "Please check your read permissions.",
                file=os.sys.stderr,
            )
            return
        except OSError as e:
            print(
                f"An unexpected OS error occurred when accessing directory '{args.directory}': {e}",
                file=os.sys.stderr,
            )
            return
    elif args.file:
        filenames = [os.path.basename(args.file)]
        base_dir = (
            os.path.dirname(args.file) or os.getcwd()
        )  # Use current working directory if path is just filename
    else:
        print(
            "Error: No directory or file specified for anime command.",
            file=os.sys.stderr,
        )
        return

    episode_data: Optional[Dict[Tuple[str, int, int], str]] = None
    # TODO: Populate episode_data if 'online' arg is present
    _process_filenames(
        filenames, base_dir, default_season=args.season, episode_data=episode_data
    )

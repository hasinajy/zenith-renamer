import os
import re
from typing import List, Optional, Tuple, Dict, Any

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


def extract_anime_info(
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

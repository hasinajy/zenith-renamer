import re
from typing import List, Optional, Tuple, Dict

EPISODE_PATTERNS = [
    r"Watch (.*?) Episode (\d+)",               # Watch Raise wa Tanin ga Ii Episode 01 English Subbed at Site Name
    r"(.*?) Episode (\d+)",                     # Raise wa Tanin ga Ii Episode 01 English Subbed at Site Name
    r"(.*?) (\d+)(.*?) Season Episode (\d+)",   # Raise wa Tanin ga Ii 1st Season Episode 01 English Subbed at Site Name
    r"(.*?) - S(\d+) - E(\d+) - (.*?)",         # Raise wa Tanin ga Ii - S01 - E01 - Episode Title
    r"(.*?) - S(\d+) - E(\d+)",                 # Raise wa Tanin ga Ii - S01 - E01
    r"(.*?) - E(\d+) - (.*?)",                  # Raise wa Tanin ga Ii - E01 - Episode Title
    r"(.*?) - E(\d+)"                           # Raise wa Tanin ga Ii - E01
]


def _process_pattern(pattern: str, match: re.Match) -> Tuple[str, Optional[int], int, Optional[str]]:
    """Process a regex match to extract episode details.

    Args:
        pattern (str): The regex pattern that matched the filename.
        match (re.Match): The match object from the regex search.

    Returns:
        Tuple[str, Optional[int], int, Optional[str]]: (series_name, season, episode, episode_title)
    """
    series_name = match.group(1).strip()
    
    if pattern == EPISODE_PATTERNS[0]:
        return series_name, None, int(match.group(2)), None
    elif pattern == EPISODE_PATTERNS[1]:
        return series_name, None, int(match.group(2)), None
    elif pattern == EPISODE_PATTERNS[2]:
        return series_name, int(match.group(2)), int(match.group(4)), None
    elif pattern == EPISODE_PATTERNS[3]:
        return series_name, int(match.group(2)), int(match.group(3)), match.group(4)
    elif pattern == EPISODE_PATTERNS[4]:
        return series_name, int(match.group(2)), int(match.group(3)), None
    elif pattern == EPISODE_PATTERNS[5]:
        return series_name, None, int(match.group(2)), match.group(3)
    elif pattern == EPISODE_PATTERNS[6]:
        return series_name, None, int(match.group(2)), None


def get_episode_info(filename: str, patterns: List[str] = EPISODE_PATTERNS) -> Tuple:
    """Extract episode information from a filename using regex patterns.

    Args:
        filename (str): The filename to parse.
        patterns (List[str]): List of regex patterns to match against (default: EPISODE_PATTERNS).

    Returns:
        Tuple: (series_name, season, episode, episode_title, filename) if matched, else empty tuple.
    """
    for pattern in patterns:
        match = re.search(pattern, filename, re.IGNORECASE)
        if match:
            series_name, season, episode, episode_title = _process_pattern(pattern, match)
            return series_name, season, episode, episode_title, filename
    return ()


def _update_all_anime_info(all_anime_info: Dict[str, Dict[int, Dict[int, Tuple[str, Optional[int], int, Optional[str], str]]]], episode_info: Tuple[str, Optional[int], int, Optional[str], str]) -> None:
    """Update the all_anime_info dictionary with episode information.

    Args:
        all_anime_info (Dict[str, Dict[int, Dict[int, Tuple[str, Optional[int], int, Optional[str], str]]]]): Nested dictionary to update.
        episode_info (Tuple[str, Optional[int], int, Optional[str], str]): Episode information to add.
    """
    if not episode_info:
        return

    series_name, season, episode, episode_title, filename = episode_info
    season_key = season or 1  # Default to season 1 if not specified

    all_anime_info.setdefault(series_name, {}).setdefault(season_key, {})[episode] = (
        series_name, season, episode, episode_title, filename
    )


def _get_local_anime_info(filenames: List[str]) -> Dict[str, Dict[int, Dict[int, Tuple[str, Optional[int], int, Optional[str], str]]]]:
    """Get anime information from local filenames.

    Args:
        filenames (List[str]): List of filenames to process.

    Returns:
        Dict[str, Dict[int, Dict[int, Tuple[str, Optional[int], int, Optional[str], str]]]]: Nested dictionary of anime information.
    """
    all_anime_info = {}
    for filename in filenames:
        episode_info = get_episode_info(filename)
        _update_all_anime_info(all_anime_info, episode_info)
    return all_anime_info


def get_all_anime_info(filenames: List[str], online: bool) -> Optional[Dict[str, Dict[int, Dict[int, Tuple[str, Optional[int], int, Optional[str], str]]]]]:
    """Get all anime information, either from local files or online (placeholder).

    Args:
        filenames (List[str]): List of filenames to process.
        online (bool): Whether to fetch data online (not implemented).

    Returns:
        Optional[Dict[str, Dict[int, Dict[int, Tuple[str, Optional[int], int, Optional[str], str]]]]]: Anime information or None if no files.
    """
    if not filenames:
        return None
    if online:
        return None  # Placeholder for online implementation
    else:
        return _get_local_anime_info(filenames)
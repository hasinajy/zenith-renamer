import re

EPISODE_PATTERNS = [
    r"Watch (.*?) Episode (\d+)",               # Watch Raise wa Tanin ga Ii Episode 01 English Subbed at Site Name
    r"(.*?) Episode (\d+)",                     # Raise wa Tanin ga Ii Episode 01 English Subbed at Site Name
    r"(.*?) (\d+)(.*?) Season Episode (\d+)",   # Raise wa Tanin ga Ii 1st Season Episode 01 English Subbed at Site Name
    r"(.*?) - S(\d+) - E(\d+) - (.*?)",         # Raise wa Tanin ga Ii - S01 - E01 - Episode Title
    r"(.*?) - S(\d+) - E(\d+)",                 # Raise wa Tanin ga Ii - S01 - E01
    r"(.*?) - E(\d+) - (.*?)",                  # Raise wa Tanin ga Ii - E01 - Episode Title
    r"(.*?) - E(\d+)"                           # Raise wa Tanin ga Ii - E01
]


def extract_fetch_info(files):
    """Extract the series name from the first matching file."""
    pass


def _get_online_anime_info(filenames):
    pass


def _process_pattern(pattern, match):
    """Process a regex match based on the pattern and return the data."""
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


def get_episode_info(filename, patterns=EPISODE_PATTERNS):
    """Match a filename against multiple patterns and return data if found."""
    
    for pattern in patterns:
        match = re.search(pattern, filename, re.IGNORECASE)
        
        if match:
            series_name, season, episode, episode_title = _process_pattern(pattern, match)
            return series_name, season, episode, episode_title, filename
    
    return ()


def _update_all_anime_info(all_anime_info: dict, episode_info: tuple):
    if not episode_info:
        return

    series_name, season, episode, episode_title, filename = episode_info
    season_key = season or 1  # Use a default season number for data consistency

    all_anime_info.setdefault(series_name, {}).setdefault(season_key, {})[episode] = (
        series_name, season, episode, episode_title, filename
    )


def _get_local_anime_info(filenames):
    all_anime_info = {}
    
    for filename in filenames:
        episode_info = get_episode_info(filename=filename)
        _update_all_anime_info(all_anime_info=all_anime_info, episode_info=episode_info)
    
    return all_anime_info


def get_all_anime_info(filenames, online):
    if not filenames:
        return None
    
    if online:
        return _get_online_anime_info(filenames=filenames)
    else:
        return _get_local_anime_info(filenames=filenames)
    
    
def get_anime_title(filename):
    series_name, _, _, _, _ = get_episode_info(filename=filename)
    return series_name
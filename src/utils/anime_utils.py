import os
import re

EPISODE_PATTERNS = [
    r"Watch (.*?) Episode (\d+)",               # Watch Raise wa Tanin ga Ii Episode 01 English Subbed at Site Name
    r"(.*?) Episode (\d+)",                     # Raise wa Tanin ga Ii Episode 01 English Subbed at Site Name
    r"(.*?) (\d+)(.*?) Season Episode (\d+)",   # Raise wa Tanin ga Ii 1st Season Episode 01 English Subbed at Site Name
    r"(.*?) - S(\d+) - E(\d+)",
    r"(.*?) - E(\d+)"
]


def _process_pattern(pattern, match, file_ext=None):
    """Process a regex match based on the pattern and return the data."""
    series_name = match.group(1).strip()
    
    if pattern == EPISODE_PATTERNS[0]:
        return (series_name, None, int(match.group(2)), file_ext)
    elif pattern == EPISODE_PATTERNS[1]:
        return (series_name, None, int(match.group(2)), file_ext)
    elif pattern == EPISODE_PATTERNS[2]:
        return (series_name, int(match.group(2)), int(match.group(4)), file_ext)
    elif pattern == EPISODE_PATTERNS[3]:
        return (series_name, int(match.group(2)), int(match.group(3)), file_ext)
    elif pattern == EPISODE_PATTERNS[4]:
        return (series_name, None, int(match.group(2)), file_ext)


def extract_anime_info(filename, patterns=EPISODE_PATTERNS):
    """Match a filename against multiple patterns and return data if found."""
    file_ext = os.path.splitext(filename)[1]
    for pattern in patterns:
        match = re.search(pattern, filename, re.IGNORECASE)
        if match:
            return _process_pattern(pattern, match, file_ext=file_ext)
        
    return (None, None, None, None)


def extract_fetch_info(files):
    """Extract the series name from the first matching file."""
    for filename in files:
        series_name, season_num, _, _ = extract_anime_info(filename)
        if series_name and season_num:
            return series_name, season_num
    return None
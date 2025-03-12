import os
from typing import List, Tuple

VIDEO_EXTENSIONS = (".mp4", ".mkv", ".ts", ".avi")
SUBTITLE_EXTENSIONS = (".srt", ".vtt", ".ass", ".sub")
VALID_EXTENSIONS = VIDEO_EXTENSIONS + SUBTITLE_EXTENSIONS


def list_video_files(path: str, valid_extensions: Tuple[str, ...] = VALID_EXTENSIONS) -> List[str]:
    """List files with valid video or subtitle extensions in the given path.

    Args:
        path (str): Directory path to list files from.
        valid_extensions (Tuple[str, ...]): Tuple of valid file extensions (default: VALID_EXTENSIONS).

    Returns:
        List[str]: List of filenames with valid extensions.
    """
    return [
        f for f in os.listdir(path)
        if f.lower().endswith(valid_extensions)
    ]
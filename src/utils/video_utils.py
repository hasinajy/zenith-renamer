import os
from typing import List, Tuple

SUBTITLE_EXTENSIONS: Tuple[str, ...] = (
    ".srt",
    ".vtt",
    ".ass",
    ".sub",
)
VIDEO_EXTENSIONS: Tuple[str, ...] = (".mp4", ".mkv", ".ts", ".avi")
RELEVANT_MEDIA_EXTENSIONS: Tuple[str, ...] = VIDEO_EXTENSIONS + SUBTITLE_EXTENSIONS


def list_media_files(
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

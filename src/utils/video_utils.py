import os

VIDEO_EXTENSION = (".mp4", ".mkv", ".ts", ".avi")
SUBTITLE_EXTENSION = (".srt", "vtt", ".ass", ".sub")
VALID_EXTENSION = VIDEO_EXTENSION + SUBTITLE_EXTENSION


def list_media_files(path, valid_extensions=VALID_EXTENSION):
    """List only the relevant files to process"""
    return [f for f in os.listdir(path) if f.lower().endswith(valid_extensions)]

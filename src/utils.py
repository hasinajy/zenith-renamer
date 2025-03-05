import argparse
import os

VIDEO_EXTENSION = (".mp4", ".mkv", ".ts", ".avi")
SUBTITLE_EXTENSION = (".srt", "vtt", ".ass", ".sub")
VALID_EXTENSION = VIDEO_EXTENSION + SUBTITLE_EXTENSION


def add_common_arguments(parser, has_online=True):
    """Add shared arguments to a parser."""
    parser.add_argument(
        "-d", "--directory",
        help="Path to the directory containing files"
    )
    parser.add_argument(
        "-f", "--file",
        help="Path to an individual file"
    )
    
    if has_online:
        parser.add_argument(
        "--online",
        action="store_false",
        help="Fetch data from an API"
    )
    
    
def handle_invalid_arguments(args):
    """Validate arguments and raise errors for invalid inputs."""
    # Check if both directory and file are provided
    has_directory = hasattr(args, "directory") and args.directory
    has_file = hasattr(args, "file") and args.file

    if has_directory and has_file:
        raise argparse.ArgumentError(
            None,
            "Cannot specify both --directory and --file; choose one."
        )

    # Validate directory if provided
    if has_directory:
        if not os.path.exists(args.directory):
            raise argparse.ArgumentError(
                None,
                "The provided directory path does not exist."
            )
        if not os.path.isdir(args.directory):
            raise argparse.ArgumentError(
                None,
                "The provided path is not a directory."
            )

    # Validate file if provided
    if has_file:
        if not os.path.exists(args.file):
            raise argparse.ArgumentError(
                None,
                "The provided file path does not exist."
            )
        if not os.path.isfile(args.file):
            raise argparse.ArgumentError(
                None,
                "The provided path is not a file."
            )
            
        
def list_media_files(path, valid_extensions=VALID_EXTENSION):
    """List only the relevant files to process"""
    return [file for file in os.listdir(path) if file.lower().endswith(valid_extensions)]
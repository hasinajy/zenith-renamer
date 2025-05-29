import argparse
import os
from typing import List, Dict, Optional, Tuple
from utils import anime_utils, video_utils


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
    series_name, _, episode_num, file_ext = anime_utils.extract_anime_info(filename)
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
        series_name, season_from_file, episode_num, _ = anime_utils.extract_anime_info(
            filename
        )

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
            filenames = video_utils.list_media_files(args.directory)
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

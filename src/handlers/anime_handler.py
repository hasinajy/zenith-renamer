import os
from typing import Optional, Tuple, Dict, List
import argparse
from utils import anime_utils, video_utils

# Type aliases for clarity
EpisodeInfo = Tuple[str, Optional[int], int, Optional[str], str]  # (series_name, season, episode, episode_title, filename)
SeasonInfo = Dict[int, EpisodeInfo]  # episode number -> episode info
SeriesInfo = Dict[int, SeasonInfo]  # season number -> season info
AllAnimeInfo = Dict[str, SeriesInfo]  # series name -> series info


def _get_anime_args(args: argparse.Namespace) -> Tuple[Optional[str], Optional[str], int, bool]:
    """Extract anime-specific arguments from the parsed args.

    Args:
        args (argparse.Namespace): Parsed command-line arguments.

    Returns:
        Tuple[Optional[str], Optional[str], int, bool]: (file, directory, season, online)
    """
    return args.file, args.directory, args.season, args.online


def _get_files_to_process(file: Optional[str], directory: Optional[str]) -> Tuple[List[str], str]:
    """Determine the list of files to process and the base directory.

    Args:
        file (Optional[str]): Path to a single file, if provided.
        directory (Optional[str]): Path to a directory containing files, if provided.

    Returns:
        Tuple[List[str], str]: (list of filenames, base directory)
    """
    filenames = []
    base_dir = ""
    
    if file:
        filenames = [os.path.basename(file)]
        base_dir = os.path.dirname(file)
    elif directory:
        try:
            filenames = video_utils.list_video_files(directory)
            base_dir = directory
        except OSError as e:
            print(f"Error accessing directory: {e}")
            return [], ""
    
    return filenames, base_dir


def _make_new_name(episode_info: EpisodeInfo, season_arg: int) -> Optional[Tuple[str, str]]:
    """Generate the new filename based on episode information.

    Args:
        episode_info (EpisodeInfo): Tuple containing (series_name, season, episode, episode_title, filename).
        season_arg (int): Season number provided via command line.

    Returns:
        Optional[Tuple[str, str]]: (old_name, new_name) if episode_info is valid, else None.
    """
    if not episode_info:
        return None
    
    series_name, season, episode, episode_title, filename = episode_info
    _, file_ext = os.path.splitext(filename)
    season_to_use = season or season_arg
    season_str = f" - S{season_to_use:02d}" if season_to_use else ""
    episode_str = f" - E{episode:02d}"
    title_str = f" - {episode_title}" if episode_title else ""
    new_name = f"{series_name}{season_str}{episode_str}{title_str}{file_ext}"
    return filename, new_name


def _rename_file(old_name: str, new_name: str, base_dir: str) -> None:
    """Rename the file from old_name to new_name in the base directory.

    Args:
        old_name (str): Current filename.
        new_name (str): Desired new filename.
        base_dir (str): Directory containing the file.
    """
    old_path = os.path.join(base_dir, old_name)
    new_path = os.path.join(base_dir, new_name)
    
    if old_path == new_path:
        print(f"Skipping {new_path}. Already renamed.")
    else:
        try:
            os.rename(old_path, new_path)
        except OSError as e:
            print(f"Error renaming {old_name}: {e}")


def _rename_episode(episode_info: EpisodeInfo, season_arg: int, base_dir: str) -> None:
    """Rename a single episode file based on its information.

    Args:
        episode_info (EpisodeInfo): Episode information tuple.
        season_arg (int): Season number provided via command line.
        base_dir (str): Base directory of the file.
    """
    if not episode_info:
        return
    
    result = _make_new_name(episode_info, season_arg)
    if result:
        old_name, new_name = result
        _rename_file(old_name, new_name, base_dir)


def _rename_season(season_info: SeasonInfo, season_arg: int, base_dir: str) -> None:
    """Rename all episodes in a season.

    Args:
        season_info (SeasonInfo): Dictionary of episode information for the season.
        season_arg (int): Season number provided via command line.
        base_dir (str): Base directory of the files.
    """
    if not season_info:
        return

    for episode in season_info:
        episode_info = season_info[episode]
        _rename_episode(episode_info, season_arg, base_dir)


def _rename_series(series_info: SeriesInfo, season_arg: int, base_dir: str) -> None:
    """Rename all seasons in a series.

    Args:
        series_info (SeriesInfo): Dictionary of season information for the series.
        season_arg (int): Season number provided via command line.
        base_dir (str): Base directory of the files.
    """
    if not series_info:
        return
    
    for season in series_info:
        season_info = series_info[season]
        _rename_season(season_info, season_arg, base_dir)


def _confirm_renaming(all_anime_info: AllAnimeInfo, season_arg: int) -> bool:
    """Confirm with the user before renaming if multiple series are detected and a season argument is provided.

    Args:
        all_anime_info (AllAnimeInfo): Dictionary containing anime information.
        season_arg (int): Season number provided via command line.

    Returns:
        bool: True if the user confirms or if no confirmation is needed, False otherwise.
    """
    if len(all_anime_info) > 1 and season_arg:
        print("The season number will be used on all anime series found.")
        user_confirmation = input("Are you sure you want to continue? (Yes/No): ")
        return user_confirmation.lower() == "yes"
    return True


def _process_files(all_anime_info: AllAnimeInfo, season_arg: int, base_dir: str) -> None:
    """Process and rename all anime files based on the provided information.

    Args:
        all_anime_info (AllAnimeInfo): Nested dictionary of anime information.
        season_arg (int): Season number provided via command line.
        base_dir (str): Base directory of the files.
    """
    if not all_anime_info:
        return

    if not _confirm_renaming(all_anime_info, season_arg):
        print("Aborting operation.")
        return

    for title in all_anime_info:
        series_info = all_anime_info[title]
        _rename_series(series_info, season_arg, base_dir)


def handle_anime(args: argparse.Namespace) -> None:
    """Handle anime file processing based on provided arguments.

    Args:
        args (argparse.Namespace): Parsed command-line arguments.
    """
    file, directory, season, online = _get_anime_args(args)
    filenames, base_dir = _get_files_to_process(file, directory)
    all_anime_info = anime_utils.get_all_anime_info(filenames, online)
    
    print("Processing anime files ...")
    print(f"Online mode: {online}")

    _process_files(all_anime_info, season, base_dir)
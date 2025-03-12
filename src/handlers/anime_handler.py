import os
from utils import anime_utils, video_utils


def _get_anime_args(args):
    return args.file, args.directory, args.season, args.online


def _get_files_to_process(file, directory):
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
            return
    
    return filenames, base_dir


def _make_new_name(episode_info: tuple, season_arg):
    if not episode_info:
        return
    
    series_name, season, episode, episode_title, filename = episode_info
    _, file_ext = os.path.splitext(filename)
    season_str = f"S{str(season or season_arg).zfill(2)}"
    episode_str = f"E{str(episode).zfill(2)}"
    
    if season and episode_title:
        new_name = (
            f"{series_name} - {season_str} - {episode_str} - {episode_title}{file_ext}"
        )
    elif episode_title:
        new_name = (
            f"{series_name} - {episode_str} - {episode_title}{file_ext}"
        )
    elif season or season_arg:
        new_name = f"{series_name} - {season_str} - {episode_str}{file_ext}"
    else:
        new_name = f"{series_name} - {episode_str}{file_ext}"

    return filename, new_name


def _rename_file(old_name, new_name, base_dir):
    old_path = os.path.join(base_dir, old_name)
    new_path = os.path.join(base_dir, new_name)
    
    if old_path == new_path:
        print(f"Skipping {new_path}. Already renamed.")
    else:
        try:
            os.rename(old_path, new_path)
        except OSError as e:
            print(f"Error renaming {old_name}: {e}")


def _rename_episode(episode_info: tuple, season_arg, base_dir):
    if not episode_info:
        return
    
    old_name, new_name = _make_new_name(episode_info=episode_info, season_arg=season_arg)
    _rename_file(old_name=old_name, new_name=new_name, base_dir=base_dir)


def _rename_season(season_info: dict, season_arg, base_dir):
    if not season_info:
        return

    season_episodes = tuple(season_info.keys())
    
    for episode in season_episodes:
        episode_info = season_info[episode]
        _rename_episode(episode_info=episode_info, season_arg=season_arg, base_dir=base_dir)


def _rename_series(series_info: dict, season_arg, base_dir):
    if not series_info:
        return
    
    series_seasons = tuple(series_info.keys())
    
    for season in series_seasons:
        season_info = series_info[season]
        _rename_season(season_info=season_info, season_arg=season_arg, base_dir=base_dir)


def _process_files(all_anime_info: dict=None, season_arg=0, base_dir=""):
    """Process a list of files for renaming with optional online data."""
    
    if len(all_anime_info.keys()) > 1 and season_arg:
        print("The season number number will be used on all anime series found.")
        user_confirmation = input("Are you sure you want to continue? (Yes/No) : ")
        
        if user_confirmation.lower() != "yes":
            print("Aborting operation.")
            return
    
    anime_titles = tuple(all_anime_info.keys())
    
    for title in anime_titles:
        series_info = all_anime_info[title]
        _rename_series(series_info=series_info, season_arg=season_arg, base_dir=base_dir)


def handle_anime(args):
    """Handle anime file processing."""
    
    file, directory, season, online = _get_anime_args(args=args)
    filenames, base_dir = _get_files_to_process(file=file, directory=directory)
    all_anime_info = anime_utils.get_all_anime_info(filenames=filenames, online=online)
    
    print("Processing anime files ...")
    print(f"Online mode: {online}")

    _process_files(all_anime_info=all_anime_info, season_arg=season, base_dir=base_dir)

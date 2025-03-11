import os
from utils import anime_utils, video_utils


def _rename_anime_file(old_path, filename, season=None, episode_title=None):
    """Rename an anime file based on its pattern and return the new name."""
    series_name, _, episode_num, file_ext = anime_utils.extract_anime_info(filename)
    season = f"S{str(season).zfill(2)}" if season else None

    try:
        if series_name and episode_num and file_ext:
            episode_num = f"E{str(episode_num).zfill(2)}"
            
            if season and episode_title:
                new_name = (
                    f"{series_name} - {season} - {episode_num} - {episode_title}{file_ext}"
                )
            elif episode_title:
                new_name = (
                    f"{series_name} - {episode_num} - {episode_title}{file_ext}"
                )
            elif season:
                new_name = f"{series_name} - {season} - {episode_num}{file_ext}"
            else:
                new_name = f"{series_name} - {episode_num}{file_ext}"

            new_path = os.path.join(os.path.dirname(old_path), new_name)
            
            if old_path != new_path:
                os.rename(old_path, new_path)
                print(f"Renamed: {filename} -> {new_name}")
            else:
                print("Did not rename: ", new_name)
        else:
            print(f"Skipping: {filename} (no episode pattern found)")
    except OSError as e:
        print(f"Error renaming {filename}: {e}")


def _process_files(files, base_dir, season=0, episode_data=None):
    """Process a list of files for renaming with optional online data."""
    for filename in files:
        old_path = os.path.join(base_dir, filename) if base_dir else filename # Handle relative paths
        series_name, season_num, episode_num, _ = anime_utils.extract_anime_info(filename)
        season = season_num or season
        episode_title = None

        if series_name and episode_data:
            episode_title = episode_data.get((series_name, season, episode_num))
        
        _rename_anime_file(old_path, filename, season=season, episode_title=episode_title)
 

def _get_anime_args(args):
    return args.directory, args.file, args.season, args.online


def _get_files_to_process(file, directory):
    files = []
    base_dir = ""
    
    if file:
        files = [os.path.basename(file)]
        base_dir = os.path.dirname(file)
    elif directory:
        try:
            files = video_utils.list_video_files(directory)
            base_dir = directory
        except OSError as e:
            print(f"Error accessing directory: {e}")
            return
    
    return files, base_dir


def _get_episode_data(files, online):
    episode_data = None
    
    if files and online:
        series_name, season_num = anime_utils.extract_fetch_info(files)
        season = season_num or season
        if series_name:
            csv_data = video_utils.fetch_episode_data(series_name, season=season)
            episode_data = video_utils.process_episode_data(csv_data)
        else:
            print("No valid anime title found in files for online mode.")
            
    return episode_data


def handle_anime(args):
    """Handle anime file processing."""
    
    file, directory, season, online = _get_anime_args(args=args)
    files, base_dir = _get_files_to_process(file=file, directory=directory)
    episode_data = _get_episode_data(files=files, online=online)
    
    print("Processing anime files ...")
    print(f"Online mode: {online}")

    _process_files(files, base_dir, season=season, episode_data=episode_data)

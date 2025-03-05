import os
import re
import utils

EPISODE_PATTERN = r"Watch (.*?) Episode (\d+)"


def _rename_anime_file(old_path, filename, season=None, episode_title=None):
    """Rename an anime file based on its pattern and return the new name."""
    match = re.search(EPISODE_PATTERN, filename, re.IGNORECASE)

    if match:
        series_name = match.group(1).strip()
        episode_num = match.group(2).zfill(2)  # Pad to 2 digits
        file_ext = os.path.splitext(filename)[1]

        if season and episode_title:
            season_str = f"S{str(season).zfill(2)}"
            new_name = (
                f"{series_name} - {season_str} - E{episode_num} - {episode_title}{file_ext}"
            )
        elif episode_title:
            new_name = (
                f"{series_name} - E{episode_num} - {episode_title}{file_ext}"
            )
        elif season:
            season_str = f"S{str(season).zfill(2)}"
            new_name = f"{series_name} - {season_str} - E{episode_num}{file_ext}"
        else:
            new_name = f"{series_name} - E{episode_num}{file_ext}"

        new_path = os.path.join(os.path.dirname(old_path), new_name)

        try:
            os.rename(old_path, new_path)
            print(f"Renamed: {filename} -> {new_name}")
            return new_name
        except OSError as e:
            print(f"Error renaming {filename}: {e}")
            return None
    else:
        print(f"Skipping: {filename} (no episode pattern found)")
        return None


def _process_files(files, base_dir, season=None, episode_data=None):
    """Process a list of files for renaming with optional online data."""
    for filename in files:
        old_path = os.path.join(base_dir, filename) if base_dir else filename
        match = re.search(EPISODE_PATTERN, filename, re.IGNORECASE)

        if match and episode_data:
            series_name = match.group(1).strip()
            episode_num = int(match.group(2))
            effective_season = season if season else 0
            episode_title = episode_data.get((series_name, effective_season, episode_num))
            _rename_anime_file(old_path, filename, season=effective_season, episode_title=episode_title)
        else:
            _rename_anime_file(old_path, filename, season=season)


def _get_series_name(files):
    """Extract the series name from the first matching file."""
    for filename in files:
        match = re.search(EPISODE_PATTERN, filename, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


def handle_anime(args):
    """Handle anime file processing."""
    print("Processing anime files ...")

    # Determine files to process
    base_dir = ""
    files = []
    if args.directory:
        try:
            files = utils.list_media_files(args.directory)
            base_dir = args.directory
        except OSError as e:
            print(f"Error accessing directory: {e}")
            return
    elif args.file:
        files = [os.path.basename(args.file)]
        base_dir = os.path.dirname(args.file) or ""  # Handle relative paths

    # Fetch episode data if online mode is enabled
    episode_data = None
    if args.online and files:
        series_name = _get_series_name(files)
        if series_name:
            csv_data = utils.fetch_episode_data(series_name, season=args.season)
            episode_data = utils.process_episode_data(csv_data)
        else:
            print("No valid anime title found in files for online mode.")

    # Process the files
    _process_files(files, base_dir, season=args.season, episode_data=episode_data)

    print(f"Online mode: {args.online}")
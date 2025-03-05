# src/handlers/anime_handler.py
import os
import re
import utils


def _rename_anime_file(old_path, filename, season=None):
    """Rename an anime file based on its pattern and return the new name."""
    match = re.search(r"Watch (.*?) Episode (\d+)", filename, re.IGNORECASE)

    if match:
        series_name = match.group(1).strip()
        episode_num = match.group(2).zfill(2)  # Pad to 2 digits
        file_ext = os.path.splitext(filename)[1]

        if season is not None:
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
            print(f"Error renaming {filename}: {e}", file=os.stderr)
            return None
    else:
        print(f"Skipping: {filename} (no episode pattern found)")
        return None


def handle_anime(args):
    """Handle anime file processing."""
    print("Processing anime files ...")

    if args.directory:
        try:
            files = utils.list_media_files(args.directory)
            for filename in files:
                old_path = os.path.join(args.directory, filename)
                _rename_anime_file(old_path, filename, season=args.season)
        except OSError as e:
            print(f"Error accessing directory: {e}", file=os.stderr)

    if args.file:
        _rename_anime_file(args.file, os.path.basename(args.file), season=args.season)

    print(f"Online mode: {args.online}")
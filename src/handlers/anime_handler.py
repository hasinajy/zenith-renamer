import os
import re
import utils


def handle_anime(args):
    """Handle anime file processing."""
    print("Processing anime files ...")

    if args.directory:
        try:
            files = utils.list_media_files(args.directory)
            for filename in files:
                match = re.search(
                    r"Watch (.*?) Episode (\d+)", filename, re.IGNORECASE
                )

                if match:
                    series_name = match.group(1).strip()
                    episode_num = match.group(2).zfill(2)  # Pad to 2 digits
                    # Get the file extension
                    file_ext = os.path.splitext(filename)[1]
                    new_name = f"{series_name} - E{episode_num}{file_ext}"
                    old_path = os.path.join(args.directory, filename)
                    new_path = os.path.join(args.directory, new_name)

                    try:
                        os.rename(old_path, new_path)
                        print(f"Renamed: {filename} -> {new_name}")
                    except OSError as e:
                        print(f"Error renaming {filename}: {e}", file=os.stderr)
                else:
                    print(f"Skipping: {filename} (no episode pattern found)")
        except OSError as e:
            print(f"Error accessing directory: {e}", file=os.stderr)

    if args.file:
        print(f"File: {args.file}")

    print(f"Online mode: {args.online}")
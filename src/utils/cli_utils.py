import argparse
import os


def add_common_arguments(parser: argparse.ArgumentParser, has_online: bool = True):
    """
    Adds shared command-line arguments to an argparse parser.

    These arguments typically include options for specifying input paths
    (either a directory or a single file) and an optional online mode.

    Args:
        parser: The argparse.ArgumentParser or subparser object to which
                the arguments will be added.
        has_online: A boolean flag. If True, the '--online' argument
                    is added, allowing fetching data from an API.
    """
    parser.add_argument("-f", "--file", help="Path to an individual file")
    parser.add_argument(
        "-d", "--directory", help="Path to the directory containing files"
    )

    if has_online:
        parser.add_argument(
            "--online", action="store_true", help="Fetch data from an API"
        )


def handle_invalid_arguments(args: argparse.Namespace):
    """
    Validates the combination and existence of provided command-line arguments.

    This function checks for common argument errors, such as:
    -   Specifying both a directory and a file.
    -   Ensuring provided directory paths exist and are indeed directories.
    -   Ensuring provided file paths exist and are indeed files.

    Args:
        args: An argparse.Namespace object containing the parsed command-line arguments.

    Raises:
        argparse.ArgumentError: If any invalid argument combination or path issue is found.
    """
    is_directory_provided = args.directory
    is_file_provided = args.file

    if is_directory_provided and is_file_provided:
        raise argparse.ArgumentError(
            None, "Cannot specify both --file and --directory; please choose one."
        )

    # Validate directory if provided
    if is_directory_provided:
        if not os.path.exists(args.directory):
            raise argparse.ArgumentError(
                None, f"The provided directory path does not exist: '{args.directory}'"
            )
        if not os.path.isdir(args.directory):
            raise argparse.ArgumentError(
                None, f"The provided path is not a directory: '{args.directory}'"
            )

    # Validate file if provided
    if is_file_provided:
        if not os.path.exists(args.file):
            raise argparse.ArgumentError(
                None, f"The provided file path does not exist: '{args.file}'"
            )
        if not os.path.isfile(args.file):
            raise argparse.ArgumentError(
                None, f"The provided path is not a file: '{args.file}'"
            )

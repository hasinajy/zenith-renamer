import argparse
import os


def _validate_path(
    path_str: str,
    path_description: str,
    must_be_dir: bool = False,
    must_be_file: bool = False,
):
    """
    Validates a given path string for existence and optionally for type.

    Args:
        path_str: The path string to validate.
        path_description: A human-readable description for error messages (e.g., "directory", "file").
        must_be_dir: If True, checks if the path is a directory.
        must_be_file: If True, checks if the path is a file.

    Raises:
        argparse.ArgumentError: If validation fails.
    """
    if not os.path.exists(path_str):
        raise argparse.ArgumentError(
            None, f"The provided {path_description} path does not exist: '{path_str}'"
        )
    if must_be_dir and not os.path.isdir(path_str):
        raise argparse.ArgumentError(
            None,
            f"The provided {path_description} path is not a directory: '{path_str}'",
        )
    if must_be_file and not os.path.isfile(path_str):
        raise argparse.ArgumentError(
            None, f"The provided {path_description} path is not a file: '{path_str}'"
        )


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
    if args.directory and args.file:
        raise argparse.ArgumentError(
            None, "Cannot specify both --file and --directory; please choose one."
        )

    # Validate directory if provided
    if args.directory:
        _validate_path(args.directory, "directory", must_be_dir=True)

    # Validate file if provided
    if args.file:
        _validate_path(args.file, "file", must_be_file=True)

    # Validate config file if provided
    if hasattr(args, "config") and args.config:
        _validate_path(args.config, "configuration file", must_be_file=True)

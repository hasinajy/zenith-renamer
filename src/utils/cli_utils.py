import argparse
import os


def add_common_arguments(parser: argparse.ArgumentParser, has_online: bool = True) -> None:
    """Add common arguments shared across subcommands to a parser.

    Args:
        parser (argparse.ArgumentParser): The parser to add arguments to.
        has_online (bool): Whether to include the --online argument (default: True).
    """
    parser.add_argument(
        "-f", "--file",
        help="Path to an individual file"
    )
    parser.add_argument(
        "-d", "--directory",
        help="Path to the directory containing files"
    )
    
    if has_online:
        parser.add_argument(
            "--online",
            action="store_true",
            help="Fetch data from an API"
        )


def handle_invalid_arguments(args: argparse.Namespace) -> None:
    """Validate arguments and raise errors for invalid inputs.

    Args:
        args (argparse.Namespace): Parsed command-line arguments.

    Raises:
        argparse.ArgumentError: If arguments are invalid (e.g., both file and directory specified).
    """
    has_directory = hasattr(args, "directory") and args.directory
    has_file = hasattr(args, "file") and args.file

    if has_directory and has_file:
        raise argparse.ArgumentError(
            None,
            "Cannot specify both --directory and --file; choose one."
        )

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
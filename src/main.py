import argparse
import sys
import handlers
from utils import arg


def parse_arguments():
    """
    Parses command-line arguments for ZenithRenamer.

    This function sets up the command-line interface using argparse,
    defining various subcommands for different media types (anime, movie, book)
    and a general standardization command. It also includes detailed
    help messages and validation for arguments.

    Returns:
        argparse.Namespace: An object containing the parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description=(
            "ZenithRenamer: From Digital Anarchy to Media Mastery\n\n"
            "Transform your chaotic media collection into an organized "
            "masterpiece with ZenithRenamer, your personal media curator. "
            "Whether you're an anime aficionado, movie buff, or bookworm, "
            "this tool brings order and elegance to your digital life.\n\n"
            "ZenithRenamer is the ultimate tool to conquer digital disorder "
            "and elevate your media experience."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(
        dest="command", title="Commands", metavar="<command>", required=True
    )

    # Subcommand: anime
    anime_parser = subparsers.add_parser("anime", help="Standardize anime file names.")
    arg.add_common_arguments(anime_parser)
    anime_parser.add_argument(
        "-s",
        "--season",
        type=int,
        default=0,
        help="Season number to include in the filename.",
    )
    anime_parser.add_argument(
        "--title", type=str, help="Override the series title for all matched files."
    )
    anime_parser.add_argument(
        "-c",
        "--config",
        type=str,
        help="Path to an optional JSON configuration file for anime processing.",
    )

    # Subcommand: movie
    movie_parser = subparsers.add_parser("movie", help="Standardize movie file names.")
    arg.add_common_arguments(movie_parser)

    # Subcommand: book
    book_parser = subparsers.add_parser("book", help="Standardize book file names.")
    arg.add_common_arguments(book_parser)

    # Subcommand: std
    std_parser = subparsers.add_parser(
        "std", help="Standardize file names within a directory."
    )
    arg.add_common_arguments(std_parser, has_online=False)
    std_parser.add_argument(
        "--creative", action="store_true", help="Generate random names."
    )

    args = parser.parse_args()
    arg.handle_invalid_arguments(args)
    return args


def main():
    """
    Entry point for ZenithRenamer CLI.

    This function parses command-line arguments and dispatches to the
    appropriate handler based on the provided subcommand. It also includes
    basic error handling for issues during argument parsing.
    """
    try:
        args = parse_arguments()
        if args.command in handlers.COMMAND_HANDLERS:
            handlers.COMMAND_HANDLERS[args.command](args)
        else:
            print(f"Error: Unknown command '{args.command}'.", file=sys.stderr)
            sys.exit(1)
    except argparse.ArgumentError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except SystemExit as e:
        if e.code != 0:
            print("Error during argument parsing.", file=sys.stderr)
        sys.exit(e.code)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

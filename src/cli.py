import argparse
import sys
import utils
import handlers


def parse_arguments():
    """Parses command-line arguments for ZenithRenamer."""
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
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(
        dest="command",
        title="Commands",
        metavar=""
    )

    # Subcommand: anime
    anime_parser = subparsers.add_parser("anime", help="Standardize anime file names")
    utils.add_common_arguments(anime_parser)

    # Subcommand: movie
    movie_parser = subparsers.add_parser("movie", help="Standardize movie file names")
    utils.add_common_arguments(movie_parser)

    # Subcommand: book
    book_parser = subparsers.add_parser("book", help="Standardize book file names")
    utils.add_common_arguments(book_parser)

    # Subcommand: std
    std_parser = subparsers.add_parser("std", help="Standardize file names within a directory")
    utils.add_common_arguments(std_parser, has_online=False)
    std_parser.add_argument(
        "--creative",
        action="store_false",
        help="Generate random names"
    )

    args = parser.parse_args()

    # Check for no subcommand
    if args.command is None:
        parser.print_help()
        sys.exit(0)

    # Validate arguments
    utils.handle_invalid_arguments(args)

    return args


def main():
    """Entry point for ZenithRenamer CLI."""
    try:
        args = parse_arguments()
        handlers.COMMAND_HANDLERS[args.command](args)
    except argparse.ArgumentError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
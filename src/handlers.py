def handle_anime(args):
    """Handle anime file processing."""
    print("Processing anime files ...")
    if args.directory:
        print(f"Directory: {args.directory}")
    if args.file:
        print(f"File: {args.file}")
    print(f"Online mode: {args.online}")


def handle_movie(args):
    """Handle movie file processing."""
    print("Processing movie files ...")
    if args.directory:
        print(f"Directory: {args.directory}")
    if args.file:
        print(f"File: {args.file}")
    print(f"Online mode: {args.online}")


def handle_book(args):
    """Handle book file processing."""
    print("Processing book files ...")
    if args.directory:
        print(f"Directory: {args.directory}")
    if args.file:
        print(f"File: {args.file}")
    print(f"Online mode: {args.online}")


def handle_std(args):
    """Handle standard file processing."""
    print("Processing standard files ...")
    if args.directory:
        print(f"Directory: {args.directory}")
    if args.file:
        print(f"File: {args.file}")
    print(f"Creative mode: {args.creative}")


COMMAND_HANDLERS = {
    "anime": handle_anime,
    "movie": handle_movie,
    "book": handle_book,
    "std": handle_std
}
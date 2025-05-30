def handle_std(args):
    """Handle standard file processing."""
    print("Processing standard files ...")
    if args.directory:
        print(f"Directory: {args.directory}")
    if args.file:
        print(f"File: {args.file}")
    print(f"Creative mode: {args.creative}")
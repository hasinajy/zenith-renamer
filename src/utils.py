def add_common_arguments(parser):
    """Add shared arguments to a parser."""
    parser.add_argument(
        "-d", "--directory",
        help="Path to the directory containing files"
    )
    parser.add_argument(
        "-f", "--file",
        help="Path to an individual file"
    )
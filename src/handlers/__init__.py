from .anime import AnimeHandler
from .movie import handle_movie
from .book import handle_book
from .standard import handle_std


def run_anime_handler(args):
    """Instantiates and runs the AnimeHandler."""
    AnimeHandler(args).handle()


COMMAND_HANDLERS = {
    "anime": run_anime_handler,
    "movie": handle_movie,
    "book": handle_book,
    "std": handle_std,
}

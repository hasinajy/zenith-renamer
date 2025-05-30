from .anime import handle_anime
from .movie import handle_movie
from .book import handle_book
from .standard import handle_std

COMMAND_HANDLERS = {
    "anime": handle_anime,
    "movie": handle_movie,
    "book": handle_book,
    "std": handle_std,
}

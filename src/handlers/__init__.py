from .anime_handler import handle_anime
from .movie_handler import handle_movie
from .book_handler import handle_book
from .std_handler import handle_std


COMMAND_HANDLERS = {
    "anime": handle_anime,
    "movie": handle_movie,
    "book": handle_book,
    "std": handle_std
}
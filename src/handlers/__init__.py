from .anime_handler import AnimeHandler
from .movie_handler import MovieHandler
from .book_handler import BookHandler
from .std_handler import StdHandler

COMMAND_HANDLERS = {
    "anime": AnimeHandler,
    "movie": MovieHandler,
    "book": BookHandler,
    "std": StdHandler
}
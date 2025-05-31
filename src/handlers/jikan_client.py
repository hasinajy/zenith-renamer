import csv
import os
import time
import re
from typing import List, Dict, Any, Optional

try:
    from jikanpy import Jikan, APIException  # type: ignore
except ImportError:
    print(
        "Error: jikanpy library is not installed. Please install it to use --online features for anime."
    )
    print("You can typically install it using: pip install jikanpy-v4")
    # Re-raise to prevent JikanFetcher instantiation if jikanpy is missing critical parts
    # Or, handle this more gracefully in AnimeHandler by checking for JikanFetcher availability.
    # For now, if Jikan or APIException can't be imported, JikanFetcher() will fail.
    Jikan = None  # type: ignore
    APIException = None  # type: ignore


def sanitize_filename(name: str) -> str:
    """Sanitizes a string to be used as a valid filename."""
    name = re.sub(r'[<>:"/\\|?*]', "_", name)  # Replace invalid chars with underscore
    name = re.sub(r"\s+", " ", name).strip()  # Normalize whitespace
    return name


class JikanFetcher:
    """
    A client to fetch anime data from the Jikan API (MyAnimeList unofficial API).
    """

    def __init__(self, ratelimit_sleep: float = 2.0):
        """
        Initializes the JikanFetcher.

        Args:
            ratelimit_sleep: Seconds to sleep between Jikan API calls to respect rate limits.

        Raises:
            ImportError: If Jikan library is not available.
        """
        if Jikan is None:
            raise ImportError(
                "Jikan library could not be imported. Cannot create JikanFetcher."
            )
        self.jikan = Jikan()
        self.ratelimit_sleep = ratelimit_sleep  # Jikan API has rate limits

    def _make_api_call(self, api_call_func, *args, **kwargs):
        """Wrapper for Jikan API calls with rate limiting and error handling."""
        try:
            time.sleep(self.ratelimit_sleep)  # Respect rate limits
            return api_call_func(*args, **kwargs)
        except APIException as e:  # type: ignore # APIException might be None if import failed
            print(f"Jikan API Error: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred during Jikan API call: {e}")
            return None

    def search_anime_id(self, series_title: str) -> Optional[int]:
        """
        Searches for an anime by its title and returns its MyAnimeList ID.

        Args:
            series_title: The title of the anime series to search for.

        Returns:
            The MyAnimeList ID (mal_id) of the first search result, or None if not found or an error occurs.
        """
        print(f"Searching for anime ID for '{series_title}'...")
        search_results = self._make_api_call(
            self.jikan.search,  # type: ignore # self.jikan might be None if init failed due to import
            search_type="anime",
            query=series_title,
            parameters={"limit": 1},
        )

        if search_results and "data" in search_results and search_results["data"]:
            mal_id = search_results["data"][0].get("mal_id")
            if mal_id:
                print(f"Found MAL ID: {mal_id} for '{series_title}'.")
                return int(mal_id)
            print(f"No MAL ID found in search results for '{series_title}'.")
            return None
        print(f"No search results found for '{series_title}'.")
        return None

    def fetch_anime_episodes(self, anime_id: int) -> List[Dict[str, Any]]:
        """
        Fetches all episodes for a given anime MyAnimeList ID using jikanpy-v4's auto-pagination.

        Args:
            anime_id: The MyAnimeList ID of the anime.

        Returns:
            A list of dictionaries, where each dictionary contains details of an episode.
            Returns an empty list if no episodes are found or an error occurs.
        """
        print(f"Fetching all episodes for anime ID: {anime_id}...")
        episodes_data = self._make_api_call(self.jikan.anime, id=anime_id, extension="episodes")  # type: ignore

        if episodes_data and "data" in episodes_data and episodes_data["data"]:
            print(
                f"Fetched {len(episodes_data['data'])} episodes for anime ID {anime_id}."
            )
            return episodes_data["data"]

        print(f"No episodes found or error fetching episodes for anime ID {anime_id}.")
        return []

    def save_episodes_to_csv(
        self,
        series_title_for_filename: str,
        episodes: List[Dict[str, Any]],
        output_dir: str,
    ) -> Optional[str]:
        """Saves episode data to a CSV file."""
        if not episodes:
            print("No episode data to save.")
            return None

        sanitized_series_title = sanitize_filename(series_title_for_filename)
        csv_filename = f"{sanitized_series_title}_episodes_jikan.csv"
        csv_filepath = os.path.join(output_dir, csv_filename)
        headers = [
            "Episode MAL ID",
            "Episode Title",
            "Title Japanese",
            "Title Romanji",
            "Aired Date",
        ]

        try:
            os.makedirs(output_dir, exist_ok=True)
            with open(csv_filepath, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
                for episode in episodes:
                    writer.writerow(
                        [
                            episode.get("mal_id"),
                            episode.get("title"),
                            episode.get("title_japanese"),
                            episode.get("title_romanji"),
                            (
                                episode.get("aired", "").split("T")[0]
                                if episode.get("aired")
                                else None
                            ),
                        ]
                    )
            print(f"Successfully saved Jikan episode data to '{csv_filepath}'")
            return csv_filepath
        except IOError as e:
            print(f"Error writing CSV file '{csv_filepath}': {e}")
            return None

    def fetch_and_save_anime_data_to_csv(
        self, series_title: str, output_dir: str
    ) -> Optional[str]:
        """Fetches anime ID, then all its episodes, and saves them to a CSV file."""
        anime_id = self.search_anime_id(series_title)
        if anime_id is None:
            return None
        episodes = self.fetch_anime_episodes(anime_id)
        if not episodes:
            return None
        return self.save_episodes_to_csv(series_title, episodes, output_dir)

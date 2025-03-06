import csv
import os
import utils
import google.generativeai  as genai
from io import StringIO
from dotenv import load_dotenv

VIDEO_EXTENSION = (".mp4", ".mkv", ".ts", ".avi")
SUBTITLE_EXTENSION = (".srt", "vtt", ".ass", ".sub")
VALID_EXTENSION = VIDEO_EXTENSION + SUBTITLE_EXTENSION

        
def list_media_files(path, valid_extensions=VALID_EXTENSION):
    """List only the relevant files to process"""
    return [
        f for f in os.listdir(path)
        if f.lower().endswith(valid_extensions)
    ]
    
    
def fetch_episode_data(anime_title, season=None):
    """Fetch episode data from Gemini 2.0 Flash API for the given anime title."""
    load_dotenv()
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")

    # Modify title with season if provided
    query_title = f"{anime_title} - Season {season}" if season else anime_title

    # Use the provided prompt
    prompt = (
        f"Generate a CSV file listing all episodes of the anime [{query_title}] "
        "in the following format:\n\n"
        "Anime Title,Season,Episode,Episode Title\n"
        f"{query_title},S##,E##,Episode Title\n"
        f"{query_title},S##,E##,Episode Title\n"
        "...\n\n"
        "Requirements:\n\n"
        "Keep spaces in titles and episode titles but remove invalid filename characters (\\, /, :, *, ?, \", <, >, |).\n"
        "Season data should be empty if the anime has only one season.\n"
        "Use the official episode titles.\n"
        "Ensure consistency in formatting (e.g., E01, E02, ... E10 instead of E1, E2, ...).\n"
        "Output only the CSV content, without additional text or explanations."
    )

    try:
        response = model.generate_content(prompt)
        csv_data = response.text.strip()
        
        # Remove Markdown code block if present
        if csv_data.startswith("```csv"):
            csv_data = csv_data.replace("```csv", "").replace("```", "").strip()
        
        csv_data = utils.remove_special_characters(csv_data)    # Clean up invalid filename characters from the CSV data
        return csv_data
    except Exception as e:
        print(f"Error fetching episode data from Gemini API: {e}")
        return ""


def process_episode_data(csv_data):
    """Process CSV episode data into a dictionary."""
    episode_dict = {}
    csv_file = StringIO(csv_data)
    reader = csv.DictReader(csv_file)

    for row in reader:
        season = int(row["Season"].lstrip("S")) if row["Season"] else 0  # Remove 'S' prefix
        episode_num = int(row["Episode"].lstrip("E"))  # Remove 'E' prefix
        key = (row["Anime Title"], season, episode_num)
        episode_dict[key] = row["Episode Title"]

    return episode_dict

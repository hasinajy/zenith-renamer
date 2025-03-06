import re


def remove_special_characters(text):
    """Remove all characters that will raise an error when used in a filename."""
    invalid_chars = r'[<>:"/\\|?*]'
    return re.sub(invalid_chars, "", text)
import re


def remove_special_characters(text: str) -> str:
    """Remove characters that are invalid in filenames.

    Args:
        text (str): Input text to clean.

    Returns:
        str: Text with invalid characters removed.
    """
    invalid_chars = r'[<>:"/\\|?*]'
    return re.sub(invalid_chars, "", text)
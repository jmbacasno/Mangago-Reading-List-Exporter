import re
from datetime import datetime, timedelta

from .models import MangaList

def manga_list_custom_csv_dict(manga_list: MangaList) -> dict:
    csv_dict = []
    for manga_list_entry in manga_list.entries:
        entry = {}
        entry["title"] = manga_list_entry.manga.title if manga_list_entry.manga else None
        entry["url"] = manga_list_entry.manga.url if manga_list_entry.manga else None
        entry["author"] = manga_list_entry.manga.author if manga_list_entry.manga else None
        entry["genres"] = manga_list_entry.manga.genres if manga_list_entry.manga else None
        entry["alternatives"] = manga_list_entry.manga.alternatives if manga_list_entry.manga else None
        entry["cover_url"] = manga_list_entry.manga.cover_url if manga_list_entry.manga else None
        entry["summary"] = manga_list_entry.manga.summary.replace("\n", " ") if manga_list_entry.manga else None
        entry["comment"] = manga_list_entry.comment.replace("\n", " ") if manga_list_entry.comment else None
        csv_dict.append(entry)
    
    return csv_dict

def get_date_from_manga_list_timestamp(text: str) -> str:
    # Get current datetime
    current_date = datetime.now()
    
    # Compile regex patterns
    seconds_regexp = re.compile(r"(?P<seconds>\d+) seconds")
    minutes_regexp = re.compile(r"(?P<minutes>\d+) minutes")
    hours_regexp = re.compile(r"(?P<hours>\d+) hours")
    days_regexp = re.compile(r"(?P<days>\d+) days")
    date_regexp = re.compile(r"(?P<day>\d{2}) (?P<month>\d{2}),(?P<year>\d{4})")
    
    # Check if the text is in the format "dd mm, yyyy"
    if date_regexp.search(text):
        month = int(date_regexp.search(text).group("month"))
        day = int(date_regexp.search(text).group("day"))
        year = int(date_regexp.search(text).group("year"))
        return f"{year}-{month:02d}-{day:02d}"
    
    # Check if the text contains days, hours, minutes, or seconds
    elif days_regexp.search(text):
        days = int(days_regexp.search(text).group("days"))
        return (current_date - timedelta(days=days)).strftime("%Y-%m-%d")
    elif hours_regexp.search(text):
        hours = int(hours_regexp.search(text).group("hours"))
        return (current_date - timedelta(hours=hours)).strftime("%Y-%m-%d")
    elif minutes_regexp.search(text):
        minutes = int(minutes_regexp.search(text).group("minutes"))
        return (current_date - timedelta(minutes=minutes)).strftime("%Y-%m-%d")
    elif seconds_regexp.search(text):
        seconds = int(seconds_regexp.search(text).group("seconds"))
        return (current_date - timedelta(seconds=seconds)).strftime("%Y-%m-%d")
    
    # Otherwise, return None
    else:
        return None

def sanitize_filename(filename: str) -> str:
    # Remove invalid characters for file names
    filename = re.sub(r"[/\\?%*:|\"<>\x7F\x00-\x1F]", "-", filename)
    
    # Limit filename length (255 is a common filesystem limit)
    if len(filename) > 255:
        filename = filename[:255]
    
    # Remove leading and trailing spaces
    filename = filename.strip()
    
    return filename

import re

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

def sanitize_filename(filename: str) -> str:
    # Remove invalid characters for file names
    filename = re.sub(r"[/\\?%*:|\"<>\x7F\x00-\x1F]", "-", filename)
    
    # Limit filename length (255 is a common filesystem limit)
    if len(filename) > 255:
        filename = filename[:255]
    
    # Remove leading and trailing spaces
    filename = filename.strip()
    
    return filename

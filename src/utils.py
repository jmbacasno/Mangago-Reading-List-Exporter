from .models import MangaList

def manga_list_to_json_dict(manga_list: MangaList) -> dict:
    json_dict = {}
    json_dict["title"] = manga_list.title
    json_dict["url"] = manga_list.url
    json_dict["creator"] = manga_list.creator
    json_dict["creation_date"] = manga_list.creation_date
    json_dict["description"] = manga_list.description
    json_dict["tags"] = manga_list.tags
    json_dict["entries"] = []

    for manga_list_entry in manga_list.entries:
        entry = {}
        entry["manga"] =  manga_list_entry.manga.__dict__ if manga_list_entry.manga else None
        entry["comment"] = manga_list_entry.comment

        json_dict["entries"].append(entry)
    
    return json_dict

def manga_list_to_csv_dict(manga_list: MangaList) -> dict:
    csv_dict = []
    for manga_list_entry in manga_list.entries:
        entry = {}
        entry["title"] = manga_list_entry.manga.title if manga_list_entry.manga else None
        entry["url"] = manga_list_entry.manga.url if manga_list_entry.manga else None
        entry["author"] = manga_list_entry.manga.author if manga_list_entry.manga else None
        entry["genres"] = manga_list_entry.manga.genres if manga_list_entry.manga else None
        entry["cover_url"] = manga_list_entry.manga.cover_url if manga_list_entry.manga else None
        entry["summary"] = manga_list_entry.manga.summary.replace("\n", " ") if manga_list_entry.manga else None

        entry["comment"] = manga_list_entry.comment.replace("\n", " ") if manga_list_entry.comment else None

        csv_dict.append(entry)
    
    return csv_dict

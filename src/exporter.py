import json
import csv
import time

from .models import MangaList
from .utils import manga_list_to_json_dict, manga_list_to_csv_dict

#file name is current date and time 01-01-2023-01-01-01
def import_data_to_json(manga_list: MangaList, path_folder: str):
    filename = f"{path_folder}/{time.strftime('%Y-%m-%d-%H-%M-%S')}.json"
    data = manga_list_to_json_dict(manga_list)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def import_data_to_csv(manga_list: MangaList, path_folder: str):
    filename = f"{path_folder}/{time.strftime('%Y-%m-%d-%H-%M-%S')}.csv"
    data = manga_list_to_csv_dict(manga_list)
    with open(filename, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["title", "url", "author", "genres", "cover_url", "summary", "comment"],
            quotechar='"',
            quoting=csv.QUOTE_ALL,
            escapechar="\\",
        )
        writer.writeheader()
        writer.writerows(data)

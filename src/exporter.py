import json
import csv
import time
from dataclasses import asdict

from .models import MangaList
from .utils import manga_list_custom_csv_dict, sanitize_filename

def export_manga_list_to_json(manga_list: MangaList, path_folder: str):
    filename = f"{path_folder}/{sanitize_filename(manga_list.title)}_{time.strftime('%Y%m%d%H%M%S')}.json"
    data = asdict(manga_list)
    if data:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

def export_manga_list_to_csv(manga_list: MangaList, path_folder: str):
    filename = f"{path_folder}/{sanitize_filename(manga_list.title)}_{time.strftime('%Y%m%d%H%M%S')}.csv"
    data = manga_list_custom_csv_dict(manga_list)
    if data:
        data_fieldnames = data[0].keys()
        with open(filename, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=data_fieldnames,
                quotechar='"',
                quoting=csv.QUOTE_ALL,
                escapechar="\\",
            )
            writer.writeheader()
            writer.writerows(data)
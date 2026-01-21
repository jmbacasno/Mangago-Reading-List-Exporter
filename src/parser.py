import re
import time
from typing import List
from bs4 import BeautifulSoup, Tag
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from urllib.parse import urlparse

from .models import Manga, MangaListEntry, MangaList

MANGA_LIST_URL_WITH_PAGE = "https://www.mangago.me/home/mangalist/{manga_list_code}/?filter=&page={page_no}"

def get_manga_list(manga_list_code: int) -> MangaList:
    try:
        options = webdriver.ChromeOptions()
        options.page_load_strategy = "eager"
        
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(10)

        driver.get(MANGA_LIST_URL_WITH_PAGE.format(manga_list_code=manga_list_code, page_no=1))

        soup = BeautifulSoup(driver.page_source, "html.parser")
        manga_list = parse_manga_list(driver, soup, manga_list_code)

        return manga_list
    finally:
        driver.quit()

def parse_manga_list(driver: webdriver.Chrome, soup: BeautifulSoup, manga_list_code: int) -> MangaList:
    # Initialize manga list
    manga_list = MangaList()

    # Set title
    title_div = soup.select_one("div.w-title")
    if isinstance(title_div, Tag):
        h1_div = title_div.find("h1")
        if isinstance(h1_div, Tag):
            manga_list.title = h1_div.get_text(strip=True)
    
    # Set url
    manga_list.url = urlparse(driver.current_url).path

    user_profile_div = soup.select_one("div.user-profile")
    if isinstance(user_profile_div, Tag):
        # Set creator
        creator_elem = user_profile_div.find("h2")
        if isinstance(creator_elem, Tag):
            manga_list.creator = creator_elem.get_text(strip=True)
        # Set creation date
        creation_elem = user_profile_div.get_text(strip=True)
        manga_list.creation_date = re.compile(r"Create: (?P<creation_date>\d{4}-\d{2}-\d{2})").search(creation_elem).group("creation_date")
    
    # Set description
    description_div = soup.select_one("div.description")
    if isinstance(description_div, Tag):
        manga_list.description = description_div.get_text(separator=" ", strip=True).replace("\xa0", " ")

    # Set tags
    content_div = description_div.find_next_sibling("div", class_="content")
    if isinstance(content_div, Tag):
        tag_links = content_div.find_all("a", class_="tag")
        if tag_links:
            manga_list.tags = [link.get_text(strip=True) for link in tag_links]

    # Get pages
    pages = 1
    pagination_div = soup.select_one("div.pagination")
    if isinstance(pagination_div, Tag):
        pages = int(pagination_div.get("total"))

    # Traverse each manga list page
    for page_no in range(1, pages + 1):
        driver.get(MANGA_LIST_URL_WITH_PAGE.format(manga_list_code=manga_list_code, page_no=page_no))
        soup = BeautifulSoup(driver.page_source, "html.parser")
        manga_list.entries += parse_manga_list_page(soup)

    return manga_list

def parse_manga_list_page(soup: BeautifulSoup) -> List[MangaListEntry]:
    manga_list_entries = []

    # Manga List Entries
    manga_divs = soup.select("div.manga.note-and-order")
    for manga_div in manga_divs:
        # Initialize manga list entry
        manga_list_entry = MangaListEntry()

        manga_link = manga_div.select_one("div.comment").find("a")
        if isinstance(manga_link, Tag):
            # Set entry title
            manga_list_entry.title = manga_link.get_text(strip=True)
            # Set entry url
            manga_list_entry.url = manga_link.get("href")

        # Set entry comment
        blockquote_div = manga_div.find("blockquote")
        if isinstance(blockquote_div, Tag):
            manga_list_entry.comment = blockquote_div.get_text(separator="\n", strip=True)
        
        manga_list_entries.append(manga_list_entry)

    return manga_list_entries

def get_manga_details(manga_url: str) -> Manga:
    try:
        options = webdriver.ChromeOptions()
        options.page_load_strategy = "eager"
        
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(10)

        driver.get(manga_url)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        manga = parse_manga_details(soup, manga_url)

        return manga
    finally:
        driver.quit()

def get_manga_from_manga_list(manga_list: MangaList) -> List[Manga]:
    try:
        options = webdriver.ChromeOptions()
        options.page_load_strategy = "eager"
        
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(10)

        mangas = parse_mangas_from_manga_list(driver, manga_list)

        return mangas
    finally:
        driver.quit()

def parse_mangas_from_manga_list(driver: webdriver.Chrome, manga_list: MangaList) -> MangaList:
    for index in range(len(manga_list.entries)):
        manga_url = manga_list.entries[index].url
        driver.get(manga_url)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        manga = parse_manga_details(soup, manga_url)
        manga_list.entries[index].manga = manga

    return manga_list

def parse_manga_details(soup: BeautifulSoup, manga_url: str) -> Manga:
    # Initialize Manga
    manga = Manga()

    # Set title
    manga.title = (title_elem.get_text(strip=True) if (title_elem := soup.find("h1")) else "Unknown Title")

    # Set url
    manga.url = manga_url

    # Set cover url
    cover_div = soup.select_one("div.left.cover")
    if isinstance(cover_div, Tag):
        cover_elem = cover_div.find("img")
        if isinstance(cover_elem, Tag) and cover_elem.get("src"):
            src = cover_elem.get("src")
            manga.cover_url = src
    
    # Details table
    details_table = soup.select_one("div.manga_right table")
    if isinstance(details_table, Tag):
        # Find all table rows and process them
        rows = details_table.find_all("tr")
        for row in rows:
            label_tag = row.find("label")
            if not isinstance(label_tag, Tag):
                continue

            label_text = label_tag.get_text(strip=True)
            
            # Set author
            if "Author:" in label_text:
                author_link = row.find("a")
                if isinstance(author_link, Tag):
                    manga.author = author_link.get_text(strip=True)
            
            # Set genres
            elif "Genre(s):" in label_text:
                genre_links = row.find_all("a")
                if genre_links:
                    manga.genres = [link.get_text(strip=True) for link in genre_links]

    # Set summary
    summary_div = soup.select_one("div.manga_summary")
    if isinstance(summary_div, Tag):
        # Remove the "Expand" button text
        expand_button = summary_div.find("div", class_="expand")
        if isinstance(expand_button, Tag):
            expand_button.decompose()
        
        manga.summary = summary_div.get_text(strip=True)
    
    return manga

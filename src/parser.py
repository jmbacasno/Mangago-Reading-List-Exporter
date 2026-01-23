import re
from typing import List

from bs4 import BeautifulSoup, Tag
from selenium import webdriver

from .models import Manga, MangaListEntry, MangaList
from .utils import get_date_from_manga_list_timestamp

MANGA_LIST_URL_WITH_PAGE = "https://www.mangago.me/home/mangalist/{manga_list_code}/?filter=&page={page_no}"

def get_manga_list_entries(driver: webdriver.Chrome, code: str, page: int) -> List[MangaListEntry]: 
    url = MANGA_LIST_URL_WITH_PAGE.format(manga_list_code=code, page_no=page)
    driver.get(url)
    manga_list_page_soup = BeautifulSoup(driver.page_source, "html.parser")
    manga_list_entries = parse_manga_list_entries(manga_list_page_soup)
    return manga_list_entries

def get_manga(driver: webdriver.Chrome, url: str) -> Manga:
    driver.get(url)
    manga_soup = BeautifulSoup(driver.page_source, "html.parser")
    manga = parse_manga(manga_soup)
    manga.url = url
    return manga

def set_manga_for_manga_list_entry(driver: webdriver.Chrome, manga_list_entry: MangaListEntry):
    manga = get_manga(driver, manga_list_entry.url)
    manga_list_entry.manga = manga

def parse_manga_list_info(soup: BeautifulSoup):
    # Initialize manga list
    manga_list = MangaList()

    # Set title
    title_div = soup.select_one("div.w-title")
    if isinstance(title_div, Tag):
        h1_div = title_div.find("h1")
        if isinstance(h1_div, Tag):
            manga_list.title = h1_div.get_text(strip=True)

    user_profile_div = soup.select_one("div.user-profile")
    if isinstance(user_profile_div, Tag):
        # Set creator
        creator_elem = user_profile_div.find("h2")
        if isinstance(creator_elem, Tag):
            manga_list.creator = creator_elem.get_text(strip=True)
        
        info_text = user_profile_div.get_text(strip=True)
        if info_text:
            # Set creation date
            manga_list.creation_date = re.compile(r"Create: (?P<creation_date>\d{4}-\d{2}-\d{2})").search(info_text).group("creation_date")
            # Set last update
            manga_list.last_update = re.compile(r"Last update: (?P<last_update>\d{4}-\d{2}-\d{2})").search(info_text).group("last_update")
    
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
    pagination_div = soup.select_one("div.pagination")
    if isinstance(pagination_div, Tag):
        manga_list.pages = int(pagination_div.get("total"))

    return manga_list

def parse_manga_list_entries(soup: BeautifulSoup):
    manga_list_entries = []

    manga_divs = soup.select("div.manga.note-and-order")
    for manga_div in manga_divs:
        # Initialize manga list entry
        manga_list_entry = MangaListEntry()

        manga_link = manga_div.select_one("div.comment").find("a")
        if isinstance(manga_link, Tag):
            # Set url
            manga_list_entry.url = manga_link.get("href")

        # Set comment
        blockquote_div = manga_div.find("blockquote")
        if isinstance(blockquote_div, Tag):
            manga_list_entry.comment = blockquote_div.get_text(separator="\n", strip=True)
        
        # Set add date
        mangalist_item_ft_div = manga_div.select_one("div.mangalist_item_ft.clear")
        if isinstance(mangalist_item_ft_div, Tag):
            left_div = mangalist_item_ft_div.find(attrs={"class": "left", "style": "color:#BDBDBD"})
            if isinstance(left_div, Tag):
                date_text = left_div.get_text(strip=True)
                if date_text:
                    manga_list_entry.add_date = get_date_from_manga_list_timestamp(date_text)
        
        manga_list_entries.append(manga_list_entry)

    return manga_list_entries

def parse_manga(soup: BeautifulSoup):
    # Initialize manga
    manga = Manga()

    # Set title
    manga.title = (title_elem.get_text(strip=True) if (title_elem := soup.find("h1")) else "Unknown Title")

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
            
            # Set status
            if "Status:" in label_text:
                span_tag = label_tag.find_next_sibling("span")
                if isinstance(span_tag, Tag):
                    manga.status = span_tag.get_text(strip=True)
            
            # Set author
            elif "Author:" in label_text:
                author_link = row.find("a")
                if isinstance(author_link, Tag):
                    manga.author = author_link.get_text(strip=True)
                author_text = row.get_text(strip=True)
                # Set released year
                if author_text:
                    released_text = re.search(r"(?P<year>\d{4}) released.", author_text)
                    if released_text:
                        manga.released_year = int(released_text.group("year"))
            
            # Set genres
            elif "Genre(s):" in label_text:
                genre_links = row.find_all("a")
                if genre_links:
                    manga.genres = [link.get_text(strip=True) for link in genre_links]
            
            # Set alternative
            elif "Alternative:" in label_text:
                alternatives_text = row.get_text(strip=True)
                if alternatives_text:
                    alternatives = alternatives_text.replace("Alternative:", "").split("; ")
                    manga.alternatives = [alt.strip() for alt in alternatives]
    
    # Set rating
    rating_span = soup.select_one("span.rating_num")
    if isinstance(rating_span, Tag):
        manga.rating = rating_span.get_text(strip=True)
        if manga.rating:
            manga.rating = round(float(manga.rating), 1)
        # Set votes
        votes_link = rating_span.find_next_sibling("a")
        if isinstance(votes_link, Tag):
            votes_text = votes_link.get_text(strip=True)
            if votes_text:
                votes_num = re.search(r"(?P<votes>\d+)", votes_text)
                if votes_num:
                    manga.votes = int(votes_num.group("votes"))
    
    # Set summary
    summary_div = soup.select_one("div.manga_summary")
    if isinstance(summary_div, Tag):
        # Remove the "Expand" button text
        expand_button = summary_div.find("div", class_="expand")
        if isinstance(expand_button, Tag):
            expand_button.decompose()
        
        manga.summary = summary_div.get_text(strip=True)
    
    return manga

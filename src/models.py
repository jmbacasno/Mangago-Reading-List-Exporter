from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Manga:
    title: Optional[str] = None
    url: Optional[str] = None
    cover_url: Optional[str] = None
    author: Optional[str] = None
    genres: List[str] = field(default_factory=list)
    alternatives: List[str] = field(default_factory=list)
    summary: Optional[str] = None
    status: Optional[str] = None
    released_year: Optional[int] = None
    rating: Optional[float] = None
    votes: Optional[int] = None
    
    def __str__(self):
        if self.author:
            return f"{self.title} by {self.author}"
        return self.title

@dataclass
class MangaListEntry:
    title: Optional[str] = None
    manga: Optional[Manga] = None
    manga_url: Optional[str] = None
    comment: Optional[str] = None

@dataclass
class MangaList:
    title: Optional[str] = None
    url: Optional[str] = None
    creator: Optional[str] = None
    creation_date: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    pages: Optional[int] = 1
    entries: List[MangaListEntry] = field(default_factory=list)

    def __str__(self):
        return f"{self.title} by {self.creator} with {len(self.entries)} entries"
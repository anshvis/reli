from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Tuple

# Bucket definitions
BUCKETS: Dict[int, Tuple[str, float, float]] = {
    1: ("I didn't like it", 0.0, 3.3),
    2: ("It was OK", 3.4, 6.7),
    3: ("I liked it", 6.8, 10.0),
}

MAX_BOOKS = 100


@dataclass
class Book:
    title: str
    bucket: int
    rank_in_bucket: int = 0
    score: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> Book:
        return cls(**data)


@dataclass
class Library:
    books: List[Book] = field(default_factory=list)

    def get_bucket(self, bucket_id: int) -> List[Book]:
        """Return books in a bucket, sorted by rank_in_bucket ascending (worst to best)."""
        return sorted(
            [b for b in self.books if b.bucket == bucket_id],
            key=lambda b: b.rank_in_bucket,
        )

    def total_count(self) -> int:
        return len(self.books)

    def has_title(self, title: str) -> bool:
        return any(b.title.lower() == title.lower() for b in self.books)

    def all_sorted(self) -> List[Book]:
        """All books sorted by score descending."""
        return sorted(self.books, key=lambda b: b.score, reverse=True)

    def remove_book(self, title: str) -> Book | None:
        for i, b in enumerate(self.books):
            if b.title.lower() == title.lower():
                return self.books.pop(i)
        return None

    def to_dict(self) -> dict:
        return {"books": [b.to_dict() for b in self.books]}

    @classmethod
    def from_dict(cls, data: dict) -> Library:
        books = [Book.from_dict(bd) for bd in data.get("books", [])]
        return cls(books=books)

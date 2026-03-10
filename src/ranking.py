from __future__ import annotations

from typing import Callable, List

from .models import Book, Library, BUCKETS


def find_insertion_index(
    new_title: str,
    bucket_books: List[Book],
    ask_preference: Callable[[str, str], bool],
) -> int:
    """Binary search to find where to insert the new book.

    ask_preference(new_title, existing_title) should return True if the user
    prefers the new book over the existing one.

    bucket_books is sorted from least-liked (index 0) to most-liked (index N-1).
    """
    lo = 0
    hi = len(bucket_books)
    while lo < hi:
        mid = (lo + hi) // 2
        if ask_preference(new_title, bucket_books[mid].title):
            lo = mid + 1  # new book is better → search upper half
        else:
            hi = mid  # existing book is at least as good → search lower half
    return lo


def recalculate_scores(bucket_books: List[Book], bucket_id: int) -> None:
    """Evenly space scores across the bucket's range for all books in it."""
    label, range_min, range_max = BUCKETS[bucket_id]
    n = len(bucket_books)
    if n == 0:
        return
    if n == 1:
        bucket_books[0].score = round((range_min + range_max) / 2, 1)
        bucket_books[0].rank_in_bucket = 0
        return
    for i, book in enumerate(bucket_books):
        book.rank_in_bucket = i
        book.score = round(range_min + (range_max - range_min) * (i / (n - 1)), 1)


def insert_book(
    library: Library,
    title: str,
    bucket_id: int,
    ask_preference: Callable[[str, str], bool],
) -> Book:
    """Insert a new book into the library with proper ranking."""
    bucket_books = library.get_bucket(bucket_id)

    if len(bucket_books) == 0:
        idx = 0
    else:
        idx = find_insertion_index(title, bucket_books, ask_preference)

    new_book = Book(title=title, bucket=bucket_id)
    bucket_books.insert(idx, new_book)
    library.books.append(new_book)

    recalculate_scores(bucket_books, bucket_id)
    return new_book

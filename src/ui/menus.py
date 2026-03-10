from __future__ import annotations

from pathlib import Path

from rich.console import Console
from simple_term_menu import TerminalMenu

from ..models import Library, BUCKETS, MAX_BOOKS
from ..ranking import insert_book, recalculate_scores
from ..storage import save_library
from .display import print_rankings

console = Console()


def ask_preference(new_title: str, existing_title: str) -> bool:
    """Ask the user which book they prefer. Returns True if they prefer the new one."""
    console.print(f"\n[bold]Which do you prefer?[/bold]")
    menu = TerminalMenu(
        [new_title, existing_title],
        title="",
        menu_cursor_style=("fg_cyan", "bold"),
    )
    choice = menu.show()
    if choice is None:
        return False  # treat cancel as "existing is better"
    return choice == 0


def _choose_bucket(title: str) -> int | None:
    """Let the user pick a bucket for a book. Returns bucket_id (1-3) or None if cancelled."""
    console.print(f'\n[bold]How did you feel about "[cyan]{title}[/cyan]"?[/bold]')
    options = [
        f"I didn't like it  (0.0–3.3)",
        f"It was OK         (3.4–6.7)",
        f"I liked it        (6.8–10.0)",
        f"← Cancel",
    ]
    menu = TerminalMenu(
        options,
        menu_cursor_style=("fg_cyan", "bold"),
    )
    choice = menu.show()
    if choice is None or choice == 3:
        return None
    return choice + 1  # 0→1, 1→2, 2→3


def _add_one_book(library: Library) -> bool:
    """Walk through adding a single book. Returns True if a book was added."""
    if library.total_count() >= MAX_BOOKS:
        console.print(f"[red]You've reached the maximum of {MAX_BOOKS} books.[/red]")
        return False

    console.print("\n[bold]Add a Book[/bold]")
    try:
        title = input("  Enter book title: ").strip()
    except (EOFError, KeyboardInterrupt):
        return False

    if not title:
        console.print("[dim]No title entered.[/dim]")
        return False

    if library.has_title(title):
        console.print(f'[red]"{title}" is already in your library.[/red]')
        return False

    bucket_id = _choose_bucket(title)
    if bucket_id is None:
        console.print("[dim]Cancelled.[/dim]")
        return False

    book = insert_book(library, title, bucket_id, ask_preference)
    label, _, _ = BUCKETS[bucket_id]
    console.print(
        f'\n[green]Added "[bold]{book.title}[/bold]" → {label} (score: {book.score:.1f})[/green]'
    )
    return True


def add_single_book(library: Library, data_path: Path) -> None:
    if _add_one_book(library):
        save_library(library, data_path)


def add_multiple_books(library: Library, data_path: Path) -> None:
    console.print("\n[bold]Add Multiple Books[/bold]")
    console.print("[dim]Enter book titles one per line. Empty line to finish.[/dim]")

    titles: list[str] = []
    while True:
        try:
            line = input("  Title: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not line:
            break
        if library.has_title(line) or line.lower() in [t.lower() for t in titles]:
            console.print(f'[red]  "{line}" is a duplicate, skipping.[/red]')
            continue
        if library.total_count() + len(titles) >= MAX_BOOKS:
            console.print(f"[red]  Reached the {MAX_BOOKS} book limit.[/red]")
            break
        titles.append(line)

    if not titles:
        console.print("[dim]No books to add.[/dim]")
        return

    console.print(f"\n[bold]Now let's categorize and rank {len(titles)} book(s).[/bold]")
    added = 0
    for title in titles:
        bucket_id = _choose_bucket(title)
        if bucket_id is None:
            console.print(f'[dim]Skipped "{title}".[/dim]')
            continue
        book = insert_book(library, title, bucket_id, ask_preference)
        label, _, _ = BUCKETS[bucket_id]
        console.print(
            f'[green]  Added "[bold]{book.title}[/bold]" → {label} (score: {book.score:.1f})[/green]'
        )
        added += 1

    if added > 0:
        save_library(library, data_path)
    console.print(f"\n[bold]Done! Added {added} book(s).[/bold]")


def view_rankings_menu(library: Library) -> None:
    console.print("\n[bold]View Rankings[/bold]")
    menu = TerminalMenu(
        ["All books (single list)", "Grouped by bucket", "← Back"],
        menu_cursor_style=("fg_cyan", "bold"),
    )
    choice = menu.show()
    if choice is None or choice == 2:
        return
    print_rankings(library, grouped=(choice == 1))


def delete_book_menu(library: Library, data_path: Path) -> None:
    if library.total_count() == 0:
        console.print("\n[dim]No books to delete.[/dim]")
        return

    books_sorted = library.all_sorted()
    options = [f"{b.title} ({b.score:.1f})" for b in books_sorted] + ["← Cancel"]
    console.print("\n[bold]Delete a Book[/bold]")
    menu = TerminalMenu(
        options,
        menu_cursor_style=("fg_cyan", "bold"),
    )
    choice = menu.show()
    if choice is None or choice == len(books_sorted):
        return

    book = books_sorted[choice]
    bucket_id = book.bucket
    library.remove_book(book.title)

    bucket_books = library.get_bucket(bucket_id)
    recalculate_scores(bucket_books, bucket_id)

    save_library(library, data_path)
    console.print(f'[green]Deleted "[bold]{book.title}[/bold]".[/green]')


def rerank_book_menu(library: Library, data_path: Path) -> None:
    if library.total_count() == 0:
        console.print("\n[dim]No books to rerank.[/dim]")
        return

    books_sorted = library.all_sorted()
    options = [f"{b.title} ({b.score:.1f})" for b in books_sorted] + ["← Cancel"]
    console.print("\n[bold]Rerank a Book[/bold]")
    menu = TerminalMenu(
        options,
        menu_cursor_style=("fg_cyan", "bold"),
    )
    choice = menu.show()
    if choice is None or choice == len(books_sorted):
        return

    book = books_sorted[choice]
    title = book.title
    old_bucket = book.bucket
    old_label, _, _ = BUCKETS[old_bucket]

    # Choose new bucket (may be the same)
    bucket_id = _choose_bucket(title)
    if bucket_id is None:
        console.print("[dim]Cancelled.[/dim]")
        return

    # Remove from library
    library.remove_book(title)
    # Recalculate old bucket scores
    recalculate_scores(library.get_bucket(old_bucket), old_bucket)

    # Re-insert with fresh comparisons
    new_book = insert_book(library, title, bucket_id, ask_preference)
    label, _, _ = BUCKETS[bucket_id]
    console.print(
        f'\n[green]Reranked "[bold]{new_book.title}[/bold]" → {label} (score: {new_book.score:.1f})[/green]'
    )
    save_library(library, data_path)


def main_menu_loop(library: Library, data_path: Path) -> None:
    while True:
        count = library.total_count()
        console.print(f"\n[bold cyan]═══ Reli ({count} book{'s' if count != 1 else ''}) ═══[/bold cyan]")
        menu = TerminalMenu(
            [
                "Add a book",
                "Add multiple books",
                "View rankings",
                "Rerank a book",
                "Delete a book",
                "Quit",
            ],
            menu_cursor_style=("fg_cyan", "bold"),
        )
        choice = menu.show()

        if choice is None or choice == 5:
            console.print("[dim]Goodbye![/dim]")
            break
        elif choice == 0:
            add_single_book(library, data_path)
        elif choice == 1:
            add_multiple_books(library, data_path)
        elif choice == 2:
            view_rankings_menu(library)
        elif choice == 3:
            rerank_book_menu(library, data_path)
        elif choice == 4:
            delete_book_menu(library, data_path)

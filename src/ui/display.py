from __future__ import annotations

from rich.console import Console
from rich.table import Table
from rich.text import Text

from ..models import Library, BUCKETS

console = Console()

BUCKET_COLORS = {
    1: "red",
    2: "yellow",
    3: "green",
}


def print_rankings(library: Library, grouped: bool = False) -> None:
    if library.total_count() == 0:
        console.print("\n[dim]No books yet. Add some![/dim]\n")
        return

    if grouped:
        _print_grouped(library)
    else:
        _print_flat(library)


def _print_flat(library: Library) -> None:
    table = Table(title="Book Rankings", show_lines=False, padding=(0, 1))
    table.add_column("#", style="dim", width=4, justify="right")
    table.add_column("Title", min_width=20)
    table.add_column("Score", justify="right", width=6)
    table.add_column("Bucket", width=18)

    for i, book in enumerate(library.all_sorted(), 1):
        label, _, _ = BUCKETS[book.bucket]
        color = BUCKET_COLORS[book.bucket]
        table.add_row(
            str(i),
            book.title,
            f"{book.score:.1f}",
            Text(label, style=color),
        )

    console.print()
    console.print(table)
    console.print()


def _print_grouped(library: Library) -> None:
    for bucket_id in (3, 2, 1):
        label, range_min, range_max = BUCKETS[bucket_id]
        color = BUCKET_COLORS[bucket_id]
        bucket_books = library.get_bucket(bucket_id)

        table = Table(
            title=f"{label} ({range_min:.1f}–{range_max:.1f})",
            title_style=color,
            show_lines=False,
            padding=(0, 1),
        )
        table.add_column("#", style="dim", width=4, justify="right")
        table.add_column("Title", min_width=20)
        table.add_column("Score", justify="right", width=6)

        if not bucket_books:
            console.print(f"\n[{color}]{label}[/{color}] [dim](empty)[/dim]")
            continue

        for i, book in enumerate(reversed(bucket_books), 1):
            table.add_row(str(i), book.title, f"{book.score:.1f}")

        console.print()
        console.print(table)

    console.print()

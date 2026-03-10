from __future__ import annotations

import json
from pathlib import Path

from .models import Library


def load_library(path: Path) -> Library:
    if not path.exists():
        return Library()
    data = json.loads(path.read_text(encoding="utf-8"))
    return Library.from_dict(data)


def save_library(library: Library, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(library.to_dict(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

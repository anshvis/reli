from pathlib import Path

from .storage import load_library
from .ui.menus import main_menu_loop


def main() -> None:
    data_path = Path(__file__).resolve().parent.parent / "data" / "books.json"
    library = load_library(data_path)
    main_menu_loop(library, data_path)


if __name__ == "__main__":
    main()

# Reli

Beli for reading. A terminal app for ranking books using a Beli-style rating system. Instead of picking a number, you sort books by feel — and the app calculates scores for you.

## How It Works

1. **Pick a bucket** — When you add a book, you choose one of three reactions:
   - "I didn't like it" → scores 0.0–3.3
   - "It was OK" → scores 3.4–6.7
   - "I liked it" → scores 6.8–10.0

2. **Rank within the bucket** — If there are already books in that bucket, you'll be asked a series of "Which do you prefer?" questions (binary search) to find where the new book fits relative to the others.

3. **Scores update automatically** — All books in a bucket are evenly spaced across its score range. Every time you add or remove a book, scores recalculate so rankings stay relative.

## Setup

```bash
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```

## Usage

```bash
venv/bin/python run.py
```

Use arrow keys to navigate menus, Enter to select.

### Menu Options

- **Add a book** — Add one book at a time (enter title → pick bucket → answer comparisons)
- **Add multiple books** — Enter several titles upfront, then categorize and rank each one
- **View rankings** — See all books as a single ranked list or grouped by bucket
- **Delete a book** — Remove a book (scores in its bucket recalculate)

## Storage

Books are saved to `data/books.json` in the project directory. No database needed — supports up to 100 books.

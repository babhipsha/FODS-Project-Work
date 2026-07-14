

from collections import Counter, defaultdict
from datetime import datetime

import storage
from librarian_ops import generate_overdue_report

OVERDUE_ALERT_THRESHOLD = 2  # members with >= this many overdue loans trigger an alert


def most_popular_genres():
    """Return a Counter of genre -> number of times a book from that genre was borrowed."""
    loans = storage.load_loans()
    books = storage.load_books()
    counter = Counter()
    for loan in loans:
        book = books.get(loan["isbn"])
        genre = book.genre if book else "Unknown"
        counter[genre] += 1
    return counter


def borrowing_trend_by_month():
    """Return a dict of 'YYYY-MM' -> number of books borrowed that month."""
    loans = storage.load_loans()
    trend = defaultdict(int)
    for loan in loans:
        try:
            dt = datetime.strptime(loan["borrow_date"], "%Y-%m-%d")
        except ValueError:
            continue
        key = dt.strftime("%Y-%m")
        trend[key] += 1
    return dict(sorted(trend.items()))


def overdue_alerts():
    """Return a list of (member_name, member_id, overdue_count) for members whose overdue
    loan count meets or exceeds OVERDUE_ALERT_THRESHOLD."""
    report = generate_overdue_report()
    counts = Counter()
    names = {}
    for entry in report:
        counts[entry["member_id"]] += 1
        names[entry["member_id"]] = entry["member_name"]

    alerts = [
        (names[mid], mid, count)
        for mid, count in counts.items()
        if count >= OVERDUE_ALERT_THRESHOLD
    ]
    return sorted(alerts, key=lambda x: -x[2])


def plot_popular_genres(save_path="genre_popularity.png"):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    counter = most_popular_genres()
    if not counter:
        raise ValueError("No loan data available to plot.")

    genres, counts = zip(*counter.most_common())
    plt.figure(figsize=(8, 5))
    plt.bar(genres, counts, color="#4C72B0")
    plt.title("Most Popular Genres (by number of loans)")
    plt.xlabel("Genre")
    plt.ylabel("Times Borrowed")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()
    return save_path


def plot_borrowing_trend(save_path="borrowing_trend.png"):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    trend = borrowing_trend_by_month()
    if not trend:
        raise ValueError("No loan data available to plot.")

    months = list(trend.keys())
    counts = list(trend.values())
    plt.figure(figsize=(8, 5))
    plt.plot(months, counts, marker="o", color="#DD8452")
    plt.title("Borrowing Trend Over Time")
    plt.xlabel("Month")
    plt.ylabel("Books Borrowed")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()
    return save_path

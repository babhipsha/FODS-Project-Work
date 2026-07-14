
class Book:
    """Represents a single book in the library catalogue."""

    def __init__(self, isbn, title, author, genre="General", status="Available"):
        self.isbn = isbn.strip()
        self.title = title.strip()
        self.author = author.strip()
        self.genre = genre.strip() if genre else "General"
        self.status = status.strip()  # "Available" or "Borrowed"

    def is_available(self):
        return self.status.lower() == "available"

    def to_line(self):
        """Serialise the book to a pipe-delimited line for storage in books.txt."""
        return f"{self.isbn}|{self.title}|{self.author}|{self.genre}|{self.status}"

    @staticmethod
    def from_line(line):
        """Build a Book object from a stored line. Raises ValueError on malformed data."""
        parts = line.strip().split("|")
        if len(parts) != 5:
            raise ValueError(f"Malformed book record: {line!r}")
        isbn, title, author, genre, status = parts
        return Book(isbn, title, author, genre, status)

    def __str__(self):
        return f"[{self.isbn}] {self.title} by {self.author} ({self.genre}) - {self.status}"

"""
librarian_ops.py
Functions available only to Librarian (admin) users:
    - add_book / remove_book
    - update_member
    - generate_overdue_report
"""

from datetime import datetime

import storage
from book import Book
from exceptions import (
    DuplicateRecordError, BookNotFoundError, InvalidInputError, MemberNotFoundError
)


def add_book(isbn, title, author, genre="General"):
    if not isbn.strip() or not title.strip() or not author.strip():
        raise InvalidInputError("ISBN, title, and author are all required.")

    books = storage.load_books()
    if isbn in books:
        raise DuplicateRecordError(f"A book with ISBN {isbn} already exists.")

    books[isbn] = Book(isbn, title, author, genre, status="Available")
    storage.save_books(books)
    return books[isbn]


def remove_book(isbn):
    books = storage.load_books()
    if isbn not in books:
        raise BookNotFoundError(f"No book found with ISBN {isbn}.")
    removed = books.pop(isbn)
    storage.save_books(books)
    return removed


def update_member(member_id, name=None, email=None, role=None):
    members = storage.load_members()
    if member_id not in members:
        raise MemberNotFoundError(f"No member found with ID {member_id}.")

    member = members[member_id]
    if name:
        member.name = name.strip()
    if email:
        member.email = email.strip()
    if role:
        role = role.strip()
        if role.lower() not in ("librarian", "student"):
            raise InvalidInputError("Role must be 'Librarian' or 'Student'.")
        member.role = role.capitalize() if role.lower() == "student" else "Librarian"

    members[member_id] = member
    storage.save_members(members)
    return member


def generate_overdue_report():
    """Returns a list of dicts describing every loan that is overdue and not yet returned."""
    loans = storage.load_loans()
    members = storage.load_members()
    books = storage.load_books()
    today = datetime.now().date()

    overdue = []
    for loan in loans:
        if loan["return_date"] != "None":
            continue  # already returned
        try:
            due = datetime.strptime(loan["due_date"], "%Y-%m-%d").date()
        except ValueError:
            continue
        if due < today:
            member = members.get(loan["member_id"])
            book = books.get(loan["isbn"])
            overdue.append({
                "loan_id": loan["loan_id"],
                "member_name": member.name if member else loan["member_id"],
                "member_id": loan["member_id"],
                "book_title": book.title if book else loan["isbn"],
                "due_date": loan["due_date"],
                "days_overdue": (today - due).days,
            })
    return overdue

from datetime import datetime, timedelta

import storage
from exceptions import (
    BookNotFoundError, BookNotAvailableError, InvalidInputError, MemberNotFoundError
)

LOAN_PERIOD_DAYS = 14


def search_books(keyword):
    """Case-insensitive search across title, author, and genre."""
    keyword = keyword.strip().lower()
    if not keyword:
        raise InvalidInputError("Search keyword must not be empty.")
    books = storage.load_books()
    results = [
        b for b in books.values()
        if keyword in b.title.lower() or keyword in b.author.lower() or keyword in b.genre.lower()
    ]
    return results


def view_own_loans(member_id):
    loans = storage.load_loans()
    return [l for l in loans if l["member_id"] == member_id]


def update_own_profile(member_id, name=None, email=None):
    members = storage.load_members()
    if member_id not in members:
        raise MemberNotFoundError(f"No member found with ID {member_id}.")
    member = members[member_id]
    if name:
        member.name = name.strip()
    if email:
        member.email = email.strip()
    members[member_id] = member
    storage.save_members(members)
    return member


def borrow_book(member_id, isbn):
    books = storage.load_books()
    if isbn not in books:
        raise BookNotFoundError(f"No book found with ISBN {isbn}.")
    book = books[isbn]
    if not book.is_available():
        raise BookNotAvailableError(f"'{book.title}' is currently on loan.")

    book.status = "Borrowed"
    books[isbn] = book
    storage.save_books(books)

    loans = storage.load_loans()
    loan_id = storage.next_loan_id(loans)
    borrow_date = datetime.now().date()
    due_date = borrow_date + timedelta(days=LOAN_PERIOD_DAYS)
    loans.append({
        "loan_id": loan_id,
        "isbn": isbn,
        "member_id": member_id,
        "borrow_date": borrow_date.strftime("%Y-%m-%d"),
        "due_date": due_date.strftime("%Y-%m-%d"),
        "return_date": "None",
    })
    storage.save_loans(loans)
    return loans[-1]


def return_book(member_id, isbn):
    loans = storage.load_loans()
    target = None
    for loan in loans:
        if loan["member_id"] == member_id and loan["isbn"] == isbn and loan["return_date"] == "None":
            target = loan
            break
    if target is None:
        raise InvalidInputError("No active loan found for this member and book.")

    target["return_date"] = datetime.now().strftime("%Y-%m-%d")
    storage.save_loans(loans)

    books = storage.load_books()
    if isbn in books:
        books[isbn].status = "Available"
        storage.save_books(books)
    return target

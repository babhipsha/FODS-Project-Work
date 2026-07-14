"""
storage.py
Handles all reading/writing to the four flat-file "database" files:
    books.txt, members.txt, loans.txt, passwords.txt

Keeping I/O in one module (separate from the OOP models) demonstrates
modular design - the rest of the program never opens a file directly.
"""

import os
import hashlib
from datetime import datetime

from book import Book
from member import User
from exceptions import InvalidInputError

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
BOOKS_FILE = os.path.join(DATA_DIR, "books.txt")
MEMBERS_FILE = os.path.join(DATA_DIR, "members.txt")
LOANS_FILE = os.path.join(DATA_DIR, "loans.txt")
PASSWORDS_FILE = os.path.join(DATA_DIR, "passwords.txt")


def _ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)
    for path in (BOOKS_FILE, MEMBERS_FILE, LOANS_FILE, PASSWORDS_FILE):
        if not os.path.exists(path):
            open(path, "a").close()


def hash_password(plain_text):
    """Securely hash a password using SHA-256 with a static-but-separate salt file
    would be ideal in production; for a coursework-scale system SHA-256 hashing
    (rather than storing plain text) satisfies the 'secure credentials' requirement."""
    return hashlib.sha256(plain_text.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------- BOOKS ----

def load_books():
    _ensure_data_dir()
    books = {}
    with open(BOOKS_FILE, "r") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                book = Book.from_line(line)
                books[book.isbn] = book
            except ValueError:
                continue  # skip corrupted lines rather than crashing
    return books


def save_books(books_dict):
    _ensure_data_dir()
    with open(BOOKS_FILE, "w") as f:
        for book in books_dict.values():
            f.write(book.to_line() + "\n")


# -------------------------------------------------------------- MEMBERS ----

def load_members():
    _ensure_data_dir()
    members = {}
    with open(MEMBERS_FILE, "r") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                member = User.from_line(line)
                members[member.member_id] = member
            except ValueError:
                continue
    return members


def save_members(members_dict):
    _ensure_data_dir()
    with open(MEMBERS_FILE, "w") as f:
        for member in members_dict.values():
            f.write(member.to_line() + "\n")


# --------------------------------------------------------------- LOANS -----

def load_loans():
    """Each loan line: loan_id|isbn|member_id|borrow_date|due_date|return_date
    return_date is the literal string 'None' while the book is still out."""
    _ensure_data_dir()
    loans = []
    with open(LOANS_FILE, "r") as f:
        for line in f:
            if not line.strip():
                continue
            parts = line.strip().split("|")
            if len(parts) != 6:
                continue
            loans.append({
                "loan_id": parts[0],
                "isbn": parts[1],
                "member_id": parts[2],
                "borrow_date": parts[3],
                "due_date": parts[4],
                "return_date": parts[5],
            })
    return loans


def save_loans(loans_list):
    _ensure_data_dir()
    with open(LOANS_FILE, "w") as f:
        for loan in loans_list:
            f.write("|".join([
                loan["loan_id"], loan["isbn"], loan["member_id"],
                loan["borrow_date"], loan["due_date"], loan["return_date"],
            ]) + "\n")


def next_loan_id(loans_list):
    if not loans_list:
        return "L001"
    nums = [int(l["loan_id"][1:]) for l in loans_list if l["loan_id"][1:].isdigit()]
    return f"L{max(nums) + 1:03d}"


# ------------------------------------------------------------ PASSWORDS ----

def load_passwords():
    """Each line: member_id|username|password_hash"""
    _ensure_data_dir()
    creds = {}
    with open(PASSWORDS_FILE, "r") as f:
        for line in f:
            if not line.strip():
                continue
            parts = line.strip().split("|")
            if len(parts) != 3:
                continue
            member_id, username, pwd_hash = parts
            creds[username] = {"member_id": member_id, "password_hash": pwd_hash}
    return creds


def save_passwords(creds_dict):
    _ensure_data_dir()
    with open(PASSWORDS_FILE, "w") as f:
        for username, info in creds_dict.items():
            f.write(f"{info['member_id']}|{username}|{info['password_hash']}\n")


def add_password_entry(member_id, username, plain_text_password):
    creds = load_passwords()
    if username in creds:
        raise InvalidInputError(f"Username '{username}' is already taken.")
    creds[username] = {"member_id": member_id, "password_hash": hash_password(plain_text_password)}
    save_passwords(creds)


# ------------------------------------------------------------- HELPERS -----

def today_str():
    return datetime.now().strftime("%Y-%m-%d")

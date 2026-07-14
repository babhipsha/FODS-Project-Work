"""
auth.py
Handles login using passwords.txt, returning the matching User (Librarian or Student)
object on success.
"""

import storage
from exceptions import AuthenticationError, MemberNotFoundError


def login(username, plain_text_password):
    """Validate credentials against passwords.txt and return the logged-in User object.

    Raises AuthenticationError if the username/password combination is invalid.
    """
    if not username or not plain_text_password:
        raise AuthenticationError("Username and password must not be empty.")

    creds = storage.load_passwords()
    entry = creds.get(username)
    if entry is None:
        raise AuthenticationError("Invalid username or password.")

    hashed_attempt = storage.hash_password(plain_text_password)
    if hashed_attempt != entry["password_hash"]:
        raise AuthenticationError("Invalid username or password.")

    members = storage.load_members()
    user = members.get(entry["member_id"])
    if user is None:
        raise MemberNotFoundError(
            f"Credentials are valid but member record '{entry['member_id']}' is missing."
        )
    return user

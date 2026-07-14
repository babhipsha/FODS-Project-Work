
from exceptions import AuthorizationError


class User:
    """Base class for anyone registered in the system."""

    def __init__(self, member_id, name, email, role="Student"):
        self.member_id = member_id.strip()
        self.name = name.strip()
        self.email = email.strip()
        self.role = role.strip()

    def to_line(self):
        """Serialise to a pipe-delimited line for members.txt."""
        return f"{self.member_id}|{self.name}|{self.email}|{self.role}"

    @staticmethod
    def from_line(line):
        """Factory: builds the correct subclass (Librarian/Student) from a stored line."""
        parts = line.strip().split("|")
        if len(parts) != 4:
            raise ValueError(f"Malformed member record: {line!r}")
        member_id, name, email, role = parts
        if role.lower() == "librarian":
            return Librarian(member_id, name, email)
        return Student(member_id, name, email)

    def menu_options(self):
        """Overridden by subclasses to expose role-specific menu items."""
        raise NotImplementedError

    def __str__(self):
        return f"{self.member_id} - {self.name} ({self.role}) <{self.email}>"


class Librarian(User):
    """Admin-level user. Can manage books, members, and view overdue reports."""

    def __init__(self, member_id, name, email):
        super().__init__(member_id, name, email, role="Librarian")

    def menu_options(self):
        return [
            "Add a book",
            "Remove a book",
            "Update a member record",
            "Generate overdue report",
            "View borrowing analytics",
            "Logout",
        ]

    def check_permission(self, action):
        # Librarians are permitted to perform all administrative actions.
        return True


class Student(User):
    """Standard user. Can search books, view own loans, and edit own profile."""

    def __init__(self, member_id, name, email):
        super().__init__(member_id, name, email, role="Student")

    def menu_options(self):
        return [
            "Search for a book",
            "View my current loans",
            "Update my profile",
            "Logout",
        ]

    def check_permission(self, action):
        allowed = {"search_book", "view_own_loans", "update_own_profile"}
        if action not in allowed:
            raise AuthorizationError(
                f"Students are not permitted to perform '{action}'."
            )
        return True

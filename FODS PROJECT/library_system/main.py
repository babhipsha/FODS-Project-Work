import os
import sys

import auth
import librarian_ops
import student_ops
import analytics
from member import Librarian, Student
from exceptions import LibraryError


# ==============================
# Utility Functions
# ==============================

def clear():
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def pause():
    """Pause until user presses Enter."""
    input("\nPress Enter to continue...")


def print_header(title):
    """Display a formatted page header."""
    clear()
    print("=" * 50)
    print(title.center(50))
    print("=" * 50)


# ==============================
# Login
# ==============================

def do_login():
    print_header("LOGIN")

    username = input("Username: ").strip()

    if username.lower() == "quit":
        print("\nThank you for using the Library Resource Management System.")
        sys.exit()

    password = input("Password: ").strip()

    try:
        user = auth.login(username, password)
        print(f"\nWelcome, {user.name} ({user.role})!")
        return user

    except LibraryError as e:
        print(f"\nLogin Failed: {e}")
        return None


# ==============================
# Librarian Menu
# ==============================

def librarian_menu(user: Librarian):
    while True:
        print_header(f"LIBRARIAN MENU - {user.name}")

        for i, option in enumerate(user.menu_options(), start=1):
            print(f"{i}. {option}")

        choice = input("\nEnter your choice: ").strip()

        try:
            if choice == "1":
                add_book_flow()

            elif choice == "2":
                remove_book_flow()

            elif choice == "3":
                update_member_flow()

            elif choice == "4":
                overdue_report_flow()

            elif choice == "5":
                analytics_flow()

            elif choice == "6":
                print("\nLogging out...")
                break

            else:
                print("Invalid choice.")

        except LibraryError as e:
            print(f"\nError: {e}")

        except Exception as e:
            print(f"\nUnexpected Error: {e}")

        pause()


def add_book_flow():
    print_header("ADD BOOK")

    isbn = input("ISBN   : ").strip()
    title = input("Title  : ").strip()
    author = input("Author : ").strip()
    genre = input("Genre  : ").strip()

    if genre == "":
        genre = "General"

    book = librarian_ops.add_book(isbn, title, author, genre)

    print("\nBook Added Successfully!")
    print(book)


def remove_book_flow():
    print_header("REMOVE BOOK")

    isbn = input("Enter ISBN: ").strip()

    removed = librarian_ops.remove_book(isbn)

    print("\nBook Removed Successfully!")
    print(removed)


def update_member_flow():
    print_header("UPDATE MEMBER")

    member_id = input("Member ID : ").strip()
    name = input("New Name   : ").strip()
    email = input("New Email  : ").strip()
    role = input("New Role   : ").strip()

    member = librarian_ops.update_member(
        member_id,
        name or None,
        email or None,
        role or None
    )

    print("\nMember Updated Successfully!")
    print(member)


def overdue_report_flow():
    print_header("OVERDUE REPORT")

    report = librarian_ops.generate_overdue_report()

    if not report:
        print("No overdue books found.")
        return

    for item in report:
        print("-" * 40)
        print(f"Member : {item['member_name']}")
        print(f"ID     : {item['member_id']}")
        print(f"Book   : {item['book_title']}")
        print(f"Due    : {item['due_date']}")
        print(f"Late   : {item['days_overdue']} day(s)")


def analytics_flow():
    print_header("BORROWING ANALYTICS")

    output_folder = "charts"

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    try:
        genre_chart = analytics.plot_popular_genres(
            os.path.join(output_folder, "genre_popularity.png")
        )

        trend_chart = analytics.plot_borrowing_trend(
            os.path.join(output_folder, "borrowing_trend.png")
        )

        print(f"Genre Chart Saved : {genre_chart}")
        print(f"Trend Chart Saved : {trend_chart}")

    except ValueError as e:
        print(e)

    print("\nMost Popular Genres")
    print("-" * 25)

    for genre, count in analytics.most_popular_genres().most_common():
        print(f"{genre} : {count}")

    print("\nOverdue Alerts")
    print("-" * 25)

    alerts = analytics.overdue_alerts()

    if not alerts:
        print("No alerts.")

    for name, member_id, count in alerts:
        print(f"{name} ({member_id}) - {count} overdue book(s)")


# ==============================
# Student Menu
# ==============================

def student_menu(user: Student):
    while True:
        print_header(f"STUDENT MENU - {user.name}")

        for i, option in enumerate(user.menu_options(), start=1):
            print(f"{i}. {option}")

        choice = input("\nEnter your choice: ").strip()

        try:
            if choice == "1":
                search_book_flow()

            elif choice == "2":
                view_loans_flow(user)

            elif choice == "3":
                update_profile_flow(user)

            elif choice == "4":
                print("\nLogging out...")
                break

            else:
                print("Invalid choice.")

        except LibraryError as e:
            print(e)

        except Exception as e:
            print(e)

        pause()


def search_book_flow():
    print_header("SEARCH BOOK")

    keyword = input("Enter title, author or genre: ").strip()

    books = student_ops.search_books(keyword)

    if not books:
        print("\nNo books found.")
        return

    print("\nMatching Books")
    print("-" * 40)

    for book in books:
        print(book)
        print("-" * 40)

    isbn = input("\nEnter ISBN to borrow (Leave blank to cancel): ").strip()

    if isbn:
        member_id = input("Member ID: ").strip()

        loan = student_ops.borrow_book(member_id, isbn)

        print(f"\nBook Borrowed Successfully!")
        print(f"Due Date: {loan['due_date']}")


def view_loans_flow(user: Student):
    print_header("MY LOANS")

    loans = student_ops.view_own_loans(user.member_id)

    active = [loan for loan in loans if loan["return_date"] == "None"]

    if not active:
        print("No active loans.")
        return

    for loan in active:
        print("-" * 40)
        print(f"ISBN       : {loan['isbn']}")
        print(f"Borrowed   : {loan['borrow_date']}")
        print(f"Due Date   : {loan['due_date']}")


def update_profile_flow(user: Student):
    print_header("UPDATE PROFILE")

    name = input("New Name : ").strip()
    email = input("New Email: ").strip()

    updated = student_ops.update_own_profile(
        user.member_id,
        name or None,
        email or None
    )

    print("\nProfile Updated Successfully!")
    print(updated)


# ==============================
# Main Program
# ==============================

def main():
    print_header("LIBRARY RESOURCE MANAGEMENT SYSTEM")

    print("Type 'quit' as the username to exit.\n")

    while True:

        user = do_login()

        if user is None:
            again = input("\nTry Again? (Y/N): ").lower()

            if again != "y":
                print("\nGoodbye!")
                break

            continue

        if isinstance(user, Librarian):
            librarian_menu(user)

        elif isinstance(user, Student):
            student_menu(user)

        again = input("\nLogin as another user? (Y/N): ").lower()

        if again != "y":
            print("\nThank you for using the Library Resource Management System.")
            break


if __name__ == "__main__":
    main()
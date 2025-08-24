import csv
import json
from datetime import datetime

# -------------------------------
# Custom Exception
# -------------------------------
class InvalidUserError(Exception):
    """Exception for invalid user data."""
    pass

# -------------------------------
# User Class
# -------------------------------
class User:
    def __init__(self, name, email, age):
        if not name or not email or age <= 0:
            raise InvalidUserError("Name, email must be provided and age > 0")
        self.name = name
        self.email = email
        self.age = age

    def __repr__(self):
        return f"User(name='{self.name}', email='{self.email}', age={self.age})"

# -------------------------------
# Repository Interface
# -------------------------------
class UserRepository:
    def add_user(self, user: User):
        raise NotImplementedError

    def get_all_users(self):
        raise NotImplementedError

# -------------------------------
# In-Memory Repository
# -------------------------------
class InMemoryUserRepository(UserRepository):
    def __init__(self):
        self.users = []

    def add_user(self, user: User):
        self.users.append(user)

    def get_all_users(self):
        return self.users

# -------------------------------
# File-Based Repository
# -------------------------------
class FileUserRepository(UserRepository):
    def __init__(self, csv_file="users.csv", json_file="users.json"):
        self.csv_file = csv_file
        self.json_file = json_file

    def add_user(self, user: User):
        # CSV
        with open(self.csv_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([user.name, user.email, user.age])

        # JSON
        users_list = []
        # წაიკითხე ადრე შექმნილი JSON, თუ არსებობს
        try:
            with open(self.json_file, "r", encoding="utf-8") as f:
                users_list = json.load(f)
        except FileNotFoundError:
            users_list = []

        # ჩასვით ახალი მომხმარებელი dict–ის სახით
        users_list.append(user.__dict__)

        # ჩაწერა JSON-ში
        with open(self.json_file, "w", encoding="utf-8") as f:
            json.dump(users_list, f, indent=4, ensure_ascii=False)

    def get_all_users(self):
        users = []
        # წაიკითხე CSV, თუ არსებობს
        try:
            with open(self.csv_file, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                for row in reader:
                    if row:  # skip empty lines
                        name, email, age = row
                        users.append(User(name, email, int(age)))
        except FileNotFoundError:
            pass
        return users

# -------------------------------
# Decorator Example (Logging)
# -------------------------------
def log_action(func):
    def wrapper(*args, **kwargs):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

# -------------------------------
# User Service (Main App)
# -------------------------------
class UserService:
    def __init__(self, repository: UserRepository):
        self.repo = repository

    @log_action
    def add_user(self, name, email, age):
        try:
            user = User(name, email, age)
            self.repo.add_user(user)
            print(f"User {name} added successfully!")
        except InvalidUserError as e:
            print(f"Error: {e}")

    def list_users(self):
        users = self.repo.get_all_users()
        if not users:
            print("No users found.")
        for user in users:
            print(user)

    def export_report(self, filename="report.json"):
        users = self.repo.get_all_users()
        data = {
            "total_users": len(users),
            "users": [user.__dict__ for user in users]
        }
        # Save to JSON file
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        # Print report in console
        print(f"Report saved to {filename}")
        print("Report content:")
        print(json.dumps(data, indent=4, ensure_ascii=False))  # Console visualization

# -------------------------------
# Example Usage
# -------------------------------
if __name__ == "__main__":
    # Choose repository type
    # repo = InMemoryUserRepository()  # მხოლოდ მეხსიერებაში
    repo = FileUserRepository()       # CSV + JSON შენახვა

    service = UserService(repo)

    # Add users
    service.add_user("გიორგი", "giorgi@example.com", 23)
    service.add_user("ანა", "ana@example.com", 22)
    service.add_user("", "invalid@example.com", 25)  # triggers exception

    # List users
    print("\nAll Users:")
    service.list_users()

    # Export report and show content
    service.export_report()

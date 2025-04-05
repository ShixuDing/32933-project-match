import re
import json
import os

class User:
    _existing_emails = set()
    _id_counter = 1
    _json_file = "users.json"

    def __init__(self, first_name, last_name, email, password):
        self.__id = User._id_counter
        User._id_counter += 1

        self.__first_name = first_name.lower()
        self.__last_name = last_name.lower()
        self.__password = password
        self.__email = self.__validate_and_assign_email(email)
        self.__user_group_identifier = "student" if "student" in self.__email else "supervisor"

    def __validate_and_assign_email(self, input_email):
        pattern = r"^[a-z]+\.[a-z]+(-\d+)?@(student\.uts\.edu\.au|uts\.edu\.au)$"
        email = input_email.lower()
        base_name, domain = email.split('@')[0], email.split('@')[1]

        if not re.match(pattern, email):
            raise ValueError("Email format invalid. Expected format: firstname.lastname[@student.uts.edu.au|@uts.edu.au]")

        if email not in User._existing_emails:
            User._existing_emails.add(email)
            return email

        counter = 1
        while True:
            new_email = f"{base_name.split('-')[0]}-{counter}@{domain}"
            if new_email not in User._existing_emails:
                User._existing_emails.add(new_email)
                return new_email
            counter += 1

    def register(self):
        print(f"[User Registered] ID: {self.__id}, Name: {self.__first_name} {self.__last_name}")
        print(f"Email: {self.__email} | Group: {self.__user_group_identifier}")
        self.__save_to_json()
        return True

    def __save_to_json(self):
        user_data = {
            "id": self.__id,
            "first_name": self.__first_name,
            "last_name": self.__last_name,
            "email": self.__email,
            "password": self.__password,
            "user_group_identifier": self.__user_group_identifier
        }

        if os.path.exists(User._json_file):
            with open(User._json_file, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = []
        else:
            data = []

        data.append(user_data)

        with open(User._json_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def login(email, password):
        if not os.path.exists(User._json_file):
            print("No users registered yet.")
            return False

        with open(User._json_file, "r", encoding="utf-8") as f:
            try:
                users = json.load(f)
            except json.JSONDecodeError:
                print("User database is corrupted.")
                return False

        for user in users:
            if user["email"] == email and user["password"] == password:
                print(f"[Login Success] Welcome {user['first_name']} {user['last_name']} ({user['user_group_identifier']})!")
                return True

        print("Login failed: Invalid email or password.")
        return False

    def update_project_description(self, new_description):
        self.project_description = new_description
        print(f"Project description updated to: {self.project_description}")
        return self.project_description

# local test
if __name__ == "__main__":
    u1 = User("Alice", "Brown", "alice.brown@student.uts.edu.au", "123")
    u1.register()

    u2 = User("Bob", "Smith", "bob.smith@uts.edu.au", "789")
    u2.register()

    print("\n[尝试登录]")
    User.login("alice.brown@student.uts.edu.au", "123")     # successful
    User.login("bob.smith@uts.edu.au", "wrongpassword")     # fail
    User.login("not.exist@uts.edu.au", "123")               # not exist

from datetime import datetime as dt, timedelta
from collections import UserList
import pickle
from info import *
import os


class AbstractUI:
    def display_contacts(self, contacts):
        pass

    def display_message(self, message):
        pass

    def display_commands(self):
        pass

    def get_input(self, prompt):
        pass


class ConsoleUI(AbstractUI):
    def display_contacts(self, contacts):
        result = []
        for account in contacts:
            if account['birthday']:
                birth = account['birthday'].strftime("%d/%m/%Y")
            else:
                birth = ''
            if account['phones']:
                new_value = []
                for phone in account['phones']:
                    if phone:
                        new_value.append(phone)
                phone = ', '.join(new_value)
            else:
                phone = ''
            result.append(
                "_" * 50 + "\n" + f"Name: {account['name']} \nPhones: {phone} \nBirthday: {birth} \nEmail: {account['email']} \nStatus: {account['status']} \nNote: {account['note']}\n" + "_" * 50 + '\n')
        print('\n'.join(result))

    def display_message(self, message):
        print(message)

    def display_commands(self):
        commands = [
            "Commands:",
            "add - Add a new contact",
            "search - Search for contacts",
            "edit - Edit a contact",
            "remove - Remove a contact",
            "save - Save the address book",
            "load - Load the address book",
            "quit - Quit the program"
        ]
        print('\n'.join(commands))

    def get_input(self, prompt):
        return input(prompt)


class AddressBook(UserList):
    def __init__(self, ui):
        self.data = []
        self.counter = -1
        self.ui = ui

    def __str__(self):
        result = []
        for account in self.data:
            if account['birthday']:
                birth = account['birthday'].strftime("%d/%m/%Y")
            else:
                birth = ''
            if account['phones']:
                new_value = []
                for phone in account['phones']:
                    if phone:
                        new_value.append(phone)
                phone = ', '.join(new_value)
            else:
                phone = ''
            result.append(
                "_" * 50 + "\n" + f"Name: {account['name']} \nPhones: {phone} \nBirthday: {birth} \nEmail: {account['email']} \nStatus: {account['status']} \nNote: {account['note']}\n" + "_" * 50 + '\n')
        return '\n'.join(result)

    def __next__(self):
        phones = []
        self.counter += 1
        if self.data[self.counter]['birthday']:
            birth = self.data[self.counter]['birthday'].strftime("%d/%m/%Y")
        if self.counter == len(self.data):
            self.counter = -1
            raise StopIteration
        for number in self.data[self.counter]['phones']:
            if number:
                phones.append(number)
        result = "_" * 50 + "\n" + \
            f"Name: {self.data[self.counter]['name']} \nPhones: {', '.join(phones)} \nBirthday: {birth} \nEmail: {self.data[self.counter]['email']} \nStatus: {self.data[self.counter]['status']} \nNote: {self.data[self.counter]['note']}\n" + "_" * 50 + '\n'
        return result

    def __iter__(self):
        return self

    def __setitem__(self, index, record):
        self.data[index] = record

    def __getitem__(self, index):
        return self.data[index]

    def log(self, action):
        with open("log.txt", 'a') as log:
            log.write(dt.now().strftime(
                "%Y-%m-%d %H:%M:%S") + " - " + action + '\n')

    def add(self, record):
        self.data.append(record)
        self.log("Added contact")

    def save(self, file_name):
        with open(file_name, 'wb') as file:
            pickle.dump(self.data, file)
        self.log("Saved address book")

    def load(self, file_name):
        if os.path.exists(file_name):
            with open(file_name, 'rb') as file:
                self.data = pickle.load(file)
            self.log("Loaded address book")
        else:
            self.ui.display_message("File not found.")

    def search(self, pattern, category):
        result = []
        for account in self.data:
            if pattern.lower() in account[category].lower():
                result.append(account)
        if result:
            self.ui.display_contacts(result)
        else:
            self.ui.display_message("No contacts found.")

    def edit(self, contact_name, parameter, new_value):
        for account in self.data:
            if account['name'].lower() == contact_name.lower():
                account[parameter] = new_value
                self.log("Edited contact")
                return
        self.ui.display_message("Contact not found.")

    def remove(self, pattern):
        for account in self.data:
            if pattern.lower() in account['name'].lower():
                self.data.remove(account)
                self.log("Removed contact")
                self.ui.display_message("Contact removed.")
                return
        self.ui.display_message("Contact not found.")

    def __get_current_week(self):
        today = dt.now().date()
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
        return start_date, end_date

    def congratulate(self):
        current_week = self.__get_current_week()
        result = []
        for account in self.data:
            if account['birthday']:
                birth = account['birthday'].date()
                if current_week[0] <= birth <= current_week[1]:
                    result.append(account)
        if result:
            self.ui.display_contacts(result)
        else:
            self.ui.display_message("No birthdays this week.")


def main():
    ui = ConsoleUI()
    address_book = AddressBook(ui)

    while True:
        ui.display_commands()
        command = ui.get_input("Enter a command: ")

        if command == "add":
            name = ui.get_input("Enter name: ")
            phones = ui.get_input(
                "Enter phones (separated by comma): ").split(",")
            birthday = ui.get_input("Enter birthday (YYYY-MM-DD): ")
            email = ui.get_input("Enter email: ")
            status = ui.get_input("Enter status: ")
            note = ui.get_input("Enter note: ")

            account = {
                'name': name,
                'phones': phones,
                'birthday': dt.strptime(birthday, "%Y-%m-%d") if birthday else None,
                'email': email,
                'status': status,
                'note': note
            }

            address_book.add(account)

        elif command == "search":
            pattern = ui.get_input("Enter search pattern: ")
            category = ui.get_input(
                "Enter search category (name, email, status, note): ")

            address_book.search(pattern, category)

        elif command == "edit":
            contact_name = ui.get_input(
                "Enter the name of the contact to edit: ")
            parameter = ui.get_input(
                "Enter the parameter to edit (name, phones, birthday, email, status, note): ")
            new_value = ui.get_input("Enter the new value: ")

            address_book.edit(contact_name, parameter, new_value)

        elif command == "remove":
            pattern = ui.get_input("Enter a pattern to match contact names: ")

            address_book.remove(pattern)

        elif command == "save":
            file_name = ui.get_input("Enter file name to save: ")

            address_book.save(file_name)

        elif command == "load":
            file_name = ui.get_input("Enter file name to load: ")

            address_book.load(file_name)

        elif command == "quit":
            break

        else:
            ui.display_message("Invalid command. Please try again.")


if __name__ == "__main__":
    main()

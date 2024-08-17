import pickle
from functools import wraps
from datetime import datetime, timedelta
from collections import UserDict
from datetime import datetime


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, name):
        self.value = name


class Phone(Field):
    def __init__(self, phone):
        self.value = self.validate_phone(phone)

    def validate_phone(self, phone):
        if not phone.isdigit():
            raise ValueError("Phone number must contain only numbers")

        if len(phone) != 10:
            raise ValueError("Phone number must contain 10 digits")

        return phone


class Birthday(Field):

    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, '%d.%m.%Y')
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

    def __str__(self):
        return f"{self.value.strftime('%d.%m.%Y')}"


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def __str__(self):
        info = f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"
        if self.birthday:
            info += f", birthday: {self.birthday}"
        return info

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        try:
            validated_phone = Phone(new_phone)
        except ValueError as e:
            raise ValueError(f"New phone number is invalid: {e}")

        self.remove_phone(old_phone)
        self.phones.append(validated_phone)

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p

    def add_birthday(self, date):
        self.birthday = Birthday(date)


# import calendar // if use Saturday and Sunday


class AddressBook(UserDict):

    def __str__(self):
        lines = [str(record) for record in self.data.values()]
        return '\n'.join(lines)

    def add_record(self, record: Record):
        if record.name.value in self.data:
            raise KeyError(
                f"Record with name {record.name.value} already exists")
        else:
            self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name not in self.data:
            raise KeyError(f"Record with name {name} not found")
        else:
            del self.data[name]

    def get_upcoming_birthdays(self):
        upcoming_birthdays = []
        current_day = datetime.today().date()

        for name, record in self.data.items():
            if record.birthday:
                birthday = record.birthday.value.date()
                birthday_current_year = birthday.replace(year=current_day.year)

                next_week = current_day + timedelta(days=7)
                if current_day <= birthday_current_year <= next_week:

                    if birthday_current_year.weekday() == 5:
                        birthday_current_year += timedelta(days=2)
                    elif birthday_current_year.weekday() == 6:
                        birthday_current_year += timedelta(days=1)

                    upcoming_birthdays.append(
                        {"name": name, "birthday_date":  birthday_current_year.strftime('%d.%m.%Y')})

        return upcoming_birthdays


def input_error(func):
    @wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return f"{str(e)}"
        except TypeError:
            return "Incorrect number of arguments"
        except KeyError:
            return "Contact not found"
        except Exception as e:
            return f"{str(e)}"

    return inner


def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()


def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def change_contact(args, book: AddressBook):
    # if len(args) != 3:
    #     return "Invalid number of arguments. Usage: change [name] [old_number] [new_number]."
    name, old_phone, new_phone = args
    record = book.find(name)
    if record is None:
        return "Contact does not exist, you can add it."
    else:
        record.edit_phone(old_phone, new_phone)
        return "Phone changed."


@input_error
def show_phone(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record is None:
        return "Contact does not exist, you can add it."
    return record


@input_error
def add_birthday(args, book: AddressBook):
    if len(args) != 2:
        return "Invalid number of arguments. Use [name] [date]"
    name, date = args
    record = book.find(name)
    if record:
        record.add_birthday(date)
        return "Birthday added for this name."
    else:
        return "Contact with this name not found."


@input_error
def show_birthday(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record:
        if record.birthday:
            return record.birthday
        else:
            return "Birthday not added to this contact."
    else:
        return "Contact does not exist, you can add it"


@input_error
def birthdays(args, book: AddressBook):
    upcoming = book.get_upcoming_birthdays()
    if upcoming:
        return "\n".join([f"{item['name']}: {item['birthday_date']}" for item in upcoming])
    else:
        return "No upcoming birthdays."


def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)
        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == 'change':
            print(change_contact(args, book))
        elif command == 'phone':
            print(show_phone(args, book))
        elif command == 'all':
            print(book)
        elif command == 'add-birthday':
            print(add_birthday(args, book))
        elif command == 'show-birthday':
            print(show_birthday(args, book))
        elif command == 'birthdays':
            print(book.get_upcoming_birthdays())
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()

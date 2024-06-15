from collections import UserDict
from datetime import datetime, date, timedelta
import pickle

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, value):
        super().__init__(value)


class Phone(Field):
    def __init__(self, value):
        if not self.validate(value):
            raise ValueError('Phone number must be 10 digits long')
        super().__init__(value)
    
    
    def validate(self, value) -> bool:
        return len(value) == 10 and value.isdigit()

from datetime import datetime
    
class Birthday(Field):
    def __init__(self, value):
        self.value = self.validate(value)

    @staticmethod
    def validate(value):
        try:
            return datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
		

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
    
    def add_birthday(self, birthday):
        if self.birthday is not None:
            raise ValueError("A birthday has already been set for this record.")
        self.birthday = Birthday(birthday)


    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]
    

    def edit_phone(self, old_phone, new_phone):
        self.new_phone = Phone(new_phone)
        for phone in self.phones:
            if phone.value == old_phone:
                phone.value = new_phone
                break
    
    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"

class AddressBook(UserDict):
    def add_record(self, record):
         self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)
    def delete(self, name):
        del self.data[name]
    
    def adjust_for_weekend(self, birthday):
        weekend = birthday.weekday()
        if weekend == 5:
            return birthday + timedelta(days=2)
        if weekend == 6:
            return birthday + timedelta(days=1)
        return birthday
        

    def get_upcoming_birthdays(self, days = 7):
        today = datetime.today().date()
        upcoming_birthdays = []

        for record in self.values():
            # if (record.birthday.value - today).days <= days:
            #     birthday = birthday.replace(year=today.year + 1)
            #     upcoming_birthdays.append(birthday)
            if record.birthday:
                birthday_date = record.birthday.value
                birthday_this_year = birthday_date.replace(year=today.year)
                if birthday_this_year < today:
                    birthday_this_year = birthday_date.replace(year=today.year + 1)
                if 0 <= (birthday_this_year - today).days <= days:
                    adjusted_birthday = self.adjust_for_weekend(birthday_this_year)
                    upcoming_birthdays.append((record.name.value, adjusted_birthday))
                    #upcoming_birthdays.append(adjusted_birthday) 
             
        return upcoming_birthdays


  

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return f'{e}'
        except KeyError:
            return 'No such contact found'
        except IndexError:
            return 'Enter the argument for the command'
    return inner


@input_error
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

@input_error
def add_contact(args, book: AddressBook):
    if len(args) < 2:
        raise ValueError('Add name and phone')
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
def change_contact(args, book):
    if len(args) < 2:
        raise ValueError('Add name and new phone')
    name, new_phone = args
    if name in book:
        book[name] = new_phone
        return "Contact updated."
    else:
        return "Contact not found."

@input_error    
def show_phone(args, book):
    if len(args) < 1:
        raise ValueError('Add name')
    name = args[0]
    if name in book:
        return book[name]
    else:
        return f'Contact {name} not found'

@input_error   
def show_all(book):
    
    if book:
        return '\n'.join(f'{record}, birthday: {record.birthday}' for record in book.values())
    else:
        return 'No contacts found.'
       
@input_error
def add_birthday(args, book: AddressBook):
    if len(args) < 2:
        raise ValueError('Add name and phone')
    
    name, date = args
    record = book.find(name)
    if record:
        record.add_birthday(date)
        return 'Birthday is added'
    else:
        return 'Contact is not found'
    


@input_error
def show_birthday(args, book):
    if len(args) < 1:
        raise ValueError('Enter name')
    name = args[0]
    record = book.find(name)
    if record:
        if record.birthday:
            return f'{name}: {record.birthday}'
        else:
            return 'Birthday is not set'
    else:
        return 'Contact is not found'
        

@input_error
def birthdays(book: AddressBook):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if upcoming_birthdays:
        return 'Birthdays this week: ' + "".join(f'{name} : {date}' for name, date in upcoming_birthdays) 
    else:
        return 'There are no birthdays this week'




def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  


def main():
    book = load_data()

    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            save_data(book)
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
            print(show_all(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))
    

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(book))
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
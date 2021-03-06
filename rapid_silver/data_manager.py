"""
Data manager hold the DataManager Class for Rapid Silver.
Manages user data for a given user profile.
"""
import os
import time
from pymongo import MongoClient
from rich.table import Table
from rich.console import Console
from console import clear_console
from rapid_silver.text_art import TextArt
from rapid_silver.user import User

# instances created
color = TextArt()


class DataManager():
    """
    Manages user data and accesses the resources for the user when activated.
    Stores the users data entered. Updates the users data. It can only be used
    with the PasswordManagers credentials for the logged in user.
    """

    mongo_link = os.environ.get('MONGOLINK')
    _cluster = MongoClient(f'{mongo_link}')
    _database = _cluster['RapidSilver']
    _user_details_collection = _database['users_details']
    _to_do_collection = _database['to_do_lists']
    _inventory_collection = _database['inventory']

    def __init__(self, user_id, the_route):
        self.username = user_id
        self.results = self.check_user_details()

        if the_route == 'profile':
            if self.results is None:
                self.user = User()
                self.add_details_to_database(
                    self.username, self.user.user_details)
                self.print_welcome_back()
        elif the_route == 'to_do':
            self.open_to_do_list()
        elif the_route == 'inventory':
            self.open_inventory()

    def check_user_details(self):
        """
        Checks to see if user details already exists and returns the result.
        """
        result = self._user_details_collection.find_one({"_id": self.username})
        if result is None:
            print(color.red_fore(
                '\n\nNo profile found, create one instead\n\n'
            ))
        time.sleep(1)
        return result

    def add_details_to_database(self, user_id, dict_of_user_details):
        """
        Adds details from user class to a dict to send to the details
        collection in MongoDB.
        """
        details_to_send = {}
        details_to_send["_id"] = str(user_id)

        for key, value in dict_of_user_details.items():
            details_to_send[key] = value

        post = details_to_send
        self._user_details_collection.insert_one(post)

    def print_welcome_back(self):
        """
        Welcomes the user back and prints their details to the screen.
        """
        clear_console()
        print('\n\n\n')
        print('Welcome back ', self.username)

        print('Here are  your profile details')
        table = Table()

        user_profile = self._user_details_collection.find_one(self.username)

        table.add_column('Type', style='cyan')
        table.add_column('Details', style='yellow')

        for key, value in user_profile.items():
            table.add_row(str(key), str(value))

        console = Console()
        console.print(table)

        print(
            color.green_fore(
                '\n\n\t\tHit [ y ] + Enter to change your details'))
        print(
            color.green_fore(
                '\t\tHit [ n ] + Enter to return to options menu'))
        result = input('\nEnter selection here: ')

        if result in ('Y', 'y'):
            self.update_profile(self.username, self.user.user_details)
        elif result in ('N', 'n'):
            # heads back to the selection menu from here
            pass
        else:
            print(
                color.red_fore(
                    'INVALID INPUT. Please select a valid option'))
            time.sleep(2)
            self.print_welcome_back()  # uses recursion until input valid

    def update_profile(self, user_id, dict_of_user_details):
        """
        Takes a profile and updates that document on the Mongo Database.
        """
        user = User()  # creates a new user object
        details_to_send = user.user_details  # gets the details
        details_to_send["_id"] = str(user_id)

        for key, value in dict_of_user_details.items():
            details_to_send[key] = value

        post = details_to_send
        self._user_details_collection.update(user_id, post)  # updates database
        self.print_welcome_back()

    def open_to_do_list(self):
        """
        A user of Rapid Silver can create and update a to do list.
        Checks for existing to do list and if theres none there creates one
        for the user.
        """
        clear_console()
        to_do_list = self._to_do_collection.find_one({"_id": self.username})
        if to_do_list is None:
            # creates a to do list if none exists
            self._to_do_collection.insert_one({'_id': self.username})
            print(
                color.red_fore(
                    'There are no to do lists matching our records for you'))
            print(
                color.yellow_fore('\n Lets make one now.')
            )
            while True:
                try:
                    print(color.red_fore(
                        '\nTo leave just hit [ n ] + Enter\n'))
                    print(color.red_fore(
                        '\nTo continue hit enter'))
                    result = input(color.red_fore('Enter here: '))
                    if result in ('n', 'N'):
                        break
                    key = str(input(
                        color.purple_fore(
                            "\n\nEnter a name for the task here: ")))
                    value = str(input(
                        color.yellow_fore(
                            '\nEnter your task here:')))

                    to_move_on = str(input(
                        color.yellow_fore(
                            'To create another task hit [ y ] + Enter : ')))

                    if len(key) > 0 and len(value) > 0:
                        self._to_do_collection.update_one(
                            {"_id": self.username}, {"$set": {key: value}})
                    if to_move_on in ('Y', 'y'):
                        pass
                    else:
                        break
                except ValueError:
                    pass
                except TypeError:
                    pass
        # after a list is either found or made, print it to the terminal
        # calls to get the document again so both routes are
        # accounted for and joined back here
        to_do_list = self._to_do_collection.find_one({"_id": self.username})
        table = Table()
        table.add_column('Name', style='Magenta')
        table.add_column('Task', style='yellow')

        if to_do_list is not None:
            for key, value in to_do_list.items():
                # hides the id and username
                if key != '_id':
                    table.add_row(str(key), str(value))

            console = Console()
            console.print(table)

        print(color.red_fore(
            "\nWould you like to update your to do list?"
        ))
        print(
            "Hit [ y ] + enter to update your to do list: "
        )

        result = input(color.yellow_fore(
            'Enter your choice here, hit enter to skip: '
        ))
        color.dot_loading('Updating to do list now')
        if result in ('y', 'Y'):
            self.clear_update_to_do_list()
        else:
            pass

    def print_todo_list(self):
        """
        Prints the to do list to the terminal to view.
        """
        to_do_list = self._to_do_collection.find_one({"_id": self.username})
        table = Table()
        table.add_column('Name', style='Magenta')
        table.add_column('Task', style='yellow')

        for key, value in to_do_list.items():
            # hides the id and username
            if key != '_id':
                table.add_row(str(key), str(value))

        console = Console()
        console.print(table)

    def clear_update_to_do_list(self):
        """
        Clears or makes amendments to a to do list for a user.
        """
        clear_console()
        self.print_todo_list()

        print('\n\n\nIf you would like to empty your to do list')
        print("Please enter 'empty list' below")
        print('Hit Enter otherwise ')
        result = input(color.cyan_fore('Enter here please'))
        if result == 'empty list':
            self._to_do_collection.delete_one({"_id": self.username})
        else:
            while True:
                clear_console()
                self.print_todo_list()
                task_name = input(
                    color.yellow_fore(
                        'Enter the name of task you wish to update: '))
                the_task = input(
                    color.yellow_fore('Now begin writing your task here: '))

                self._to_do_collection.update_one(
                    {"_id": self.username}, {"$set": {task_name: the_task}})
                print('\n\nTo exit hit [ n ] + Enter ')
                print('\nEnter [ y ] to update another task ')
                result = input(color.red_fore('Enter here please: '))
                if result in ('n', 'N'):
                    break
                self.clear_update_to_do_list()  # prints again and asks

    def open_inventory(self):
        """
        A user of Rapid Silver can create and update inventory.
        Checks for existing inventory and if theres none there creates one
        for the user.
        """
        clear_console()
        inventory = self._inventory_collection.find_one({"_id": self.username})
        if inventory is None:
            # creates a inventory if none exists
            self._inventory_collection.insert_one({'_id': self.username})
            print(
                color.red_fore(
                    'There are no inventories matching our records for you'))
            print(
                color.yellow_fore('\n Lets create one now.')
            )
            while True:
                try:
                    print(color.red_fore(
                        '\nTo leave just hit [ n ] + Enter\n'))
                    print(color.red_fore(
                        '\nTo continue hit enter'))
                    result = input('Enter here: ')
                    if result in ('n', 'N'):
                        break
                    key = str(input(
                        color.purple_fore(
                            "\n\nEnter a name for the item here: ")))
                    value = str(input(
                        color.yellow_fore(
                            '\nEnter the amount here :')))

                    to_move_on = str(input(
                        color.yellow_fore(
                            'To create another item hit [ y ] + Enter : ')))

                    if len(key) > 0 and len(value) > 0:
                        self._inventory_collection.update_one(
                            {"_id": self.username}, {"$set": {key: value}})
                    if to_move_on in ('Y', 'y'):
                        pass
                    else:
                        break
                except ValueError:
                    pass
                except TypeError:
                    pass
        # after inventory is either found or created, print it to the terminal
        # calls to get the document again so both routes are
        # accounted for and joined back here
        inventory = self._inventory_collection.find_one({"_id": self.username})
        table = Table()
        table.add_column('Type', style='blue')
        table.add_column('Details', style='yellow')

        if inventory is not None:
            for key, value in inventory.items():
                # hides the id and username
                if key != '_id':
                    table.add_row(str(key), str(value))

            console = Console()
            console.print(table)

        print(color.red_fore(
            "\nWould you like to update your inventory?"
        ))
        print(
            "Hit [ y ] + enter to update your inventory: "
        )

        result = input(color.yellow_fore(
            'Enter your choice here, hit enter to skip: '
        ))
        color.money_loading('Updating inventory now')
        if result in ('y', 'Y'):
            self.clear_update_inventory()
        else:
            pass

    def print_inventory(self):
        """
        Prints the inventory to the terminal to view.
        """
        inventory = self._inventory_collection.find_one({"_id": self.username})
        table = Table()
        table.add_column('Type', style='blue')
        table.add_column('Details', style='yellow')

        for key, value in inventory.items():
            # hides the id and username
            if key != '_id':
                table.add_row(str(key), str(value))

        console = Console()
        console.print(table)

    def clear_update_inventory(self):
        """
        Clears or makes amendments to a inventory list for a user.
        """
        clear_console()
        self.print_inventory()

        print('\n\n\nIf you would like to empty your inventory')
        print("Please enter 'empty inventory' below")
        print('Hit Enter otherwise ')
        result = input(color.cyan_fore('Enter here please'))
        if result == 'empty inventory':
            self._inventory_collection.delete_one({"_id": self.username})
        else:
            while True:
                clear_console()
                self.print_inventory()
                inventory_name = input(
                    color.yellow_fore(
                        'Enter the name of item you wish to update: '))
                the_amount = input(
                    color.yellow_fore('Now begin updating amounts here: '))

                self._inventory_collection.update_one(
                    {"_id": self.username}, {
                        "$set": {inventory_name: the_amount}})
                print('\n\nTo exit hit [ n ] + Enter ')
                print('\nEnter [ y ] to update another inventory item')
                result = input('Enter here please: ')
                if result in ('n', 'N'):
                    break
                self.clear_update_inventory()  # prints again and asks

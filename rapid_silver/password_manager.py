"""Hold the password class for Rapid Silver"""
import os
import time
import random
from pymongo import MongoClient
from console import clear_console
from rapid_silver.text_art import TextArt


# instance created
color = TextArt()
class PasswordManager():
    """
    Handles the password information for the user of
    Rapid Silver.
    """
    character_dict = {
        'a': ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'],
        'b': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K',
              'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V',
              'W', 'X', 'Y', 'Z']
    }

    character_keys = ['a', 'b']
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    special_chars = ['!', '@', '#', '$', '%', '&', '*']
    user_mongo_dict = {
        "USERNAME": "",
        "PASSWORD": "",
        "COMPANY": ""
    }

    def __init__(self, account_type):

        # temporary catch claus for local development and live terminal development
        try:
            self._mongopass = os.environ.get('MONGOPASSWORD')
        except NameError:
            file = open('mongodb.txt', encoding='utf8')
            self._mongopass = file.read()
            file.close()
        except AttributeError:
            file = open('mongodb.txt', encoding='utf8')
            self._mongopass = file.read()
            file.close()

        # decides which route to take for the account type
        if account_type == 'new':
            self._username = self._set_username()
            self._set_user_password()
            self._log_in_user()
        elif account_type == 'old':
            self._get_login_details()
            self._log_in_user()

        # line long but link wont work without it formatted like this
        self.cluster = MongoClient(f"mongodb+srv://rapid_silver_educate:{self._mongopass}@rapidsilver.h5hbo.mongodb.net/myFirstDatabase?retryWrites=true&w=majority""")
        self.database = self.cluster['RapidSilver']
        self.collection = self.database['users']


    def _set_username(self):
        clear_console()
        for _ in range(8):
            print('\n')

        print('Would you like to set a username or have a username generated? y/n')
        result = input(color.cyan_fore('Enter here: '))

        if result in ('Y', 'y'):
            self._username = self._generate_username()

        elif result in ('N', 'n'):

            clear_console()
            try:

                advice = color.yellow_fore('Please include (A-Z & a-z) and at least 1 number')
                print(advice)
                username_input = input('Please enter a username: ')

                if len(username_input) < 8:
                    raise ValueError('Username must be at least 8 characters')
                if len(username_input) > 40:
                    raise ValueError('Username must be less than 40 characters')

                validation = self._check_characters_valid_in('username', username_input)
                if validation is False:
                    raise ValueError('You must include at least one number')
                # TODO: check database for conflicts in username here also

                self._username = username_input
            except ValueError as error:
                error = color.red_fore(error)
                print(error)
                time.sleep(1.5)
                self._set_username()

        else:
            print("INVALID Input received.")
            time.sleep(1.5)
            self._set_username()

        return self._username

    def _generate_username(self):
        """
        Generates a username for the user, a combination of letters
        and numbers.
        """
        username = ''
        rand_key = self.character_keys[random.randrange(1)]

        for _ in range(8):
            rand_key = self.character_keys[random.randrange(2)]
            arr = self.character_dict[rand_key]
            username += arr[random.randrange(len(arr))]
        return username

    def _set_user_password(self):
        return ''
    def _log_in_user(self):
        return ''
    def _get_login_details(self):
        return ''
    def _check_characters_valid_in(self, to_check, input_type):
        result = True
        if to_check == 'username':
            for char in input_type:
                if char in self.special_chars:
                    return False
        elif to_check == 'password':
            # for char in input_type:
            #     if char not in self.special_chars:
            #         return False
            #     if char not in ():
            #         return False
            pass
        return result
    # TODO: Create salt, pepper and hashing
    # TODO: Store inside a database
    # TODO: block user password from being stored anywhere in plain text
    # TODO: get all code and structure it properly







# leave id blank as it needs unique identifiers on each post and it current does not matter
# post = { user_name:password, "data":"company"}
# collection.insert_one(post)
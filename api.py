from typing import *
from config import *
import json
import os
from log import *

 
# user and user-related classes

class User:
    def __init__(self, id:int, data:dict={}):
        '''
        Represents a user.
        '''
        self.id: int = id
        
        self.saved_message: "str | None" = data.get('saved_message', None)

    
    def to_dict(self) -> dict:
        '''
        Converts the class to a dictionary to store in the file.
        '''
        return {
            "saved_message": self.saved_message
        }
    

class Whisper:
    def __init__(self, id:int, data:dict):
        '''
        Represents a whisper.
        '''
        self.id: int = id
        self.text: str = data['text']
        self.owner: int = data['owner']
        self.viewer: int = data['viewer']
        self.once: bool = data['once']

    
    def to_dict(self) -> dict:
        '''
        Converts the class to a dictionary to store in the file.
        '''
        return {
            "text": self.text,
            "owner": self.owner,
            "viewer": self.viewer,
            "once": self.once
        }


# manager

class Manager:
    def __init__(self, users_file:str):
        '''
        API and backend manager.
        '''
        self.users_file: str = users_file
        self.whispers: Dict[int, str] = {}

        self.reload()
        self.reload_data()


    def new(self):
        '''
        Rewrites the old database with the new one.
        '''
        self.users: Dict[int, User] = {}

        self.commit()


    def panic(self):
        '''
        Creates a duplicate of the database and creates a new one.
        '''
        log('Panic!', 'api', WARNING)

        # copying file
        if os.path.exists(self.users_file):
            os.rename(self.users_file, self.users_file+'.bak')
            log(f'Cloned user data file to {self.users_file}.bak', 'api')

        # creating a new one
        self.new()


    def reload(self):
        '''
        Reloads user data and bot data.
        '''
        # user data
        try:
            with open(self.users_file, encoding='utf-8') as f:
                data = json.load(f)
        except:
            self.panic()
            return

        self.users = {int(id): User(int(id), data) for id, data in data['users'].items()}
        self.whispers = {int(id): Whisper(int(id), data) for id, data in data['whispers'].items()}

        # saving
        self.commit()


    def reload_data(self):
        '''
        Reloads game data.
        '''
        # data
        try:
            with open(self.users_file, encoding='utf-8') as f:
                self.data = json.load(f)
        except Exception as e:
            log(f'Failed to load data file: {e}', 'api', ERROR)
            self.data = {}


    def commit(self):
        '''
        Saves user data to the file.
        '''
        data = {
            'users': {},
            'whispers': {}
        }

        # users
        for i in self.users:
            data['users'][i] = self.users[i].to_dict()

        # whispers
        for i in self.whispers:
            data['whispers'][i] = self.whispers[i].to_dict()

        # saving
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)


    def check_user(self, id:int):
        '''
        Checks if user exists in database. If not, creates one.
        '''
        if id in self.users:
            return
        
        self.users[id] = User(id)


    def get_user(self, id:int) -> User:
        '''
        Returns user by ID.

        Automatically checks the user.
        '''
        self.check_user(id)
        return self.users[id]


    def get_whisper(self, id:int) -> "Whisper | None":
        '''
        Returns whisper by message ID.

        Returns None if not found.
        '''
        if id not in self.whispers:
            return None
        
        return self.whispers[id]
    

    def save_whisper(self, id:int, text:str):
        '''
        Saves a whisper to a user.
        '''
        user = self.get_user(id)

        user.saved_message = text

        self.commit()
    

    def unsave_whisper(self, id:int):
        '''
        Removes a saved whisper.
        '''
        user = self.get_user(id)

        user.saved_message = None

        self.commit()


    def send_whisper(self, message:int, owner:int, viewer:int, text:int, once:bool):
        '''
        Adds a whisper to the database.
        '''
        self.whispers[message] = Whisper(
            message, {
                "text": text,
                "owner": owner,
                "viewer": viewer,
                "once": once
            }
        )

        self.commit()


    def remove_whisper(self, id:int):
        '''
        Removes a whisper from the database.
        '''
        if id not in self.whispers:
            return
        
        self.whispers.pop(id)

        self.commit()
from typing import *
from config import *
import json
import os
from log import *
    

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
    def __init__(self, data_file:str):
        '''
        API and backend manager.
        '''
        self.data_file: str = data_file
        self.whispers: Dict[int, str] = {}

        self.reload()


    def new(self):
        '''
        Rewrites the old database with the new one.
        '''
        self.commit()


    def panic(self):
        '''
        Creates a duplicate of the database and creates a new one.
        '''
        log('Panic!', 'api', WARNING)

        # copying file
        if os.path.exists(self.data_file):
            os.rename(self.data_file, self.data_file+'.bak')
            log(f'Cloned user data file to {self.data_file}.bak', 'api')

        # creating a new one
        self.new()


    def reload(self):
        '''
        Reloads user data and bot data.
        '''
        # user data
        try:
            with open(self.data_file, encoding='utf-8') as f:
                data = json.load(f)
        except:
            self.panic()
            return

        self.whispers = {int(id): Whisper(int(id), data) for id, data in data['whispers'].items()}

        # saving
        self.commit()


    def commit(self):
        '''
        Saves user data to the file.
        '''
        data = {
            'whispers': {i: self.whispers[i].to_dict() for i in self.whispers}
        }

        # saving
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)


    def get_whisper(self, id:int) -> "Whisper | None":
        '''
        Returns whisper by message ID.

        Returns None if not found.
        '''
        if id not in self.whispers:
            return None
        
        return self.whispers[id]


    def send_whisper(self, message:int, owner:int, viewer:int, text:str, once:bool):
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
        
        self.whispers.pop(id, None)

        self.commit()
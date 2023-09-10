import json
import os
PATH = os.path.dirname(__file__)[:-4] + "storage/users.json"

class JsonOp():
    """Json operation master"""

    def __init__(self):
        self.path = PATH
        self.key = "user_name"
        self.data_list = None

    def open(self):
        """Medthod for saving the orders store"""
        # first read the file
        try:
            with open(self.path, "r", encoding="utf-8", newline="") as file:
                self.data_list = json.load(file)
        except FileNotFoundError:
            # file is not found , so  init my data_list
            self.data_list = []

    def search(self, value):
        """searchsa an element in data_list and returns it"""
        if self.data_list is None:
            self.open()
        for item in self.data_list:
            if item[self.key] == value:
                return item
        return None

    def search_password(self, name, value):
        for item in self.data_list:
            if item[self.key] == name:
                if item["pw_token"] == value:
                    return True
        return False

    def save(self):
        """dumps data list in file"""
        if self.data_list is None:
            self.open()
            print("hey")
        try:
            with open(self.path, "w", encoding="utf-8", newline="") as file:
                json.dump(self.data_list, file, indent=2)
        except FileNotFoundError as ex:
            raise "No se ha encontrado el almacén"

"""this class encapsules a generic user"""
import json
from gestor_json import JsonOp
import os

def register_user():
    name = input("Introduzca el nombre de usuario: ")
    users_data = JsonOp()
    while users_data.search(name):
        name = input("Nombre de usuario ya existente. Introduce otro: ")

    password = input("Introduzca la contraseña: ")
    new_user = User(name, password) # TODO: cifrar password
    users_data.data_list.append(new_user.__dict__)
    users_data.save()


class User():
    def __init__(self, user_name: str,  pw_token: str): # TODO: añadir salt
        self.user_name = user_name
        self.pw_token = pw_token




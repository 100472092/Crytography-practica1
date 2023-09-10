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

def login_user():
    name = input("Introduzca el nombre de usuario: ")
    users_data = JsonOp()
    while users_data.search(name) is None:
        name = input("Nombre de usuario no existe, introduzca un usuario válido.")
    password = input("Introduzca la contraseña: ")
    tries = 3
    fallo = False
    while not users_data.search_password(name, password) and not fallo:
        tries -= 1
        if tries > 0:
            password = input("Contraseña incorrecta, " + str(tries) + " intentos restantes. Introduzca la contraseña:")
        else:
            fallo = True
    if fallo is True:
        print("Demasiados intentos fallidos.")
    else:
        print("Bienvenido de vuelta,", name)

class User():
    def __init__(self, user_name: str,  pw_token: str): # TODO: añadir salt
        self.user_name = user_name
        self.pw_token = pw_token




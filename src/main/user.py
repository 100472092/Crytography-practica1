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
    new_user = Credentials(name, password) # TODO: cifrar password
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
        return False
    else:
        user = User(name)
        print("Bienvenido de vuelta,", name)
        return user

class Credentials():
    def __init__(self, user_name: str,  pw_token: str): # TODO: añadir salt
        self.user_name = user_name
        self.pw_token = pw_token

class User():
    def __init__(self, user_name):
        self.user_name = user_name
        self.subjectlist = []
        self.examlist = []
        self.projectlist = []
    def functionality(self):
        while True:
            userchoice = input("1: AÑADIR ASIGNATURA. \n 2: AÑADIR EXAMEN. \n 3: AÑADIR FECHA DE ENTREGA. \n")
            if userchoice == "1":
                newsubject = input("Escriba asignatura a añadir: ")
                self.addSubject(newsubject)
            elif userchoice == "2":
                self.addExam()
            elif userchoice == "3":
                self.addProject()
            else:
                print("ERROR, acción no válida")
    def addSubject(self, new_subject):
        self.subjectlist.append(new_subject)
    def addExam(self):
        print(self.subjectlist)
        subject = input("Elije asignatura:")
        while subject not in self.subjectlist and subject != "0":
            subject = input("No existe la asignatura, elige una asignatura válida. Exit:0 \n")
        if subject != 0:
            fecha = input("Añada un día y hora para el examen")
            registered = False
            for item in self.examlist:
                if item[subject]:
                    item[subject].append(fecha)
                    registered = True
            if not registered:
                self.examlist.append({subject: [fecha]})
            print(self.examlist)
    def addProject(self):
        print(self.subjectlist)
        subject = input("Elije asignatura:")
        while subject not in self.subjectlist and subject != "0":
            subject = input("No existe la asignatura, elige una asignatura válida. Exit:0 \n")
        if subject != 0:
            fecha = input("Añada un día y hora para el examen")
            registered = False
            for item in self.projectlist:
                if item[subject]:
                    item[subject].append(fecha)
                    registered = True
            if not registered:
                self.projectlist.append({subject: [fecha]})
            print(self.projectlist)


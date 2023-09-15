"""this class encapsules user funtionality"""
from data_base_gestor import DataBase

def register_user(db: DataBase):
    name = input("(Escribe exit para salir)\nIntroduzca el nombre de usuario: ")
    while name != "exit" and db.search_user(name.lower()):
        name = input("(Escribe exit para salir)\nNombre de usuario ya existente. Introduce otro: ")
    if (name == "exit"):
        return
    password = input("Introduzca la contraseña: ") # TODO: CIFRAR CONTRASEÑA
    db.register_new_user(name.lower(), password)

def login_user(db: DataBase):
    tries = 3
    fallo = False

    name = input("(Escribe exit para salir)\nIntroduzca el nombre de usuario: ")
    while name != "exit" and db.search_user(name.lower()) is None:
        name = input("(Escribe exit para salir)\nNombre de usuario no existe, introduzca un usuario válido.")
    if (name == "exit"):
        return

    password = input("Introduzca la contraseña: ") # TODO: cifrar
    while not db.search_pw(password) and not fallo:
        tries -= 1
        if tries > 0:
            password = input("Contraseña incorrecta, " + str(tries) + " intentos restantes. Introduzca la contraseña:")
        else:
            fallo = True
    if fallo:
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
            userchoice = input(" 1: AÑADIR ASIGNATURA. \n 2: AÑADIR EXAMEN. \n 3: AÑADIR FECHA DE ENTREGA. \n 4: EXIT \n")
            if userchoice == "1":
                newsubject = input("Escriba asignatura a añadir: ")
                self.addSubject(newsubject)
            elif userchoice == "2":
                self.addExam()
            elif userchoice == "3":
                self.addProject()
            elif userchoice == "4":
                return
            else:
                print("ERROR, acción no válida")

    def addSubject(self, new_subject):
        self.subjectlist.append(new_subject)

    def addExam(self):
        print(self.subjectlist)
        subject = input("Elije asignatura:")
        while subject not in self.subjectlist and subject != "0":
            subject = input("No existe la asignatura, elige una asignatura válida. Exit:0 \n")
        if subject != "0":
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

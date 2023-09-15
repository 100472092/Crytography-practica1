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

class User():
    def __init__(self, user_name):
        self.user_name = user_name

    def functionality(self, db):
        while True:
            userchoice = input(" 1: AÑADIR ASIGNATURA. \n 2: AÑADIR EXAMEN. \n 3: AÑADIR FECHA DE ENTREGA. \n 4: EXIT \n")
            match userchoice:
                case "1":
                    self.addSubject()
                case "2":
                    self.addExam()
                case "3":
                    self.addProject()
                case "4":
                    return
                case _:
                    print("Error: Acción no válidad")

    def addSubject(self):
        new_subject = input("Escriba asignatura a añadir: ")


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

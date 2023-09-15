"""this class encapsules user funtionality"""
from data_base_gestor import DataBase

def register_user():
    db = DataBase()
    name = input("(Escribe exit para salir)\nIntroduzca el nombre de usuario: ")
    while name != "exit" and db.search_user(name.lower()):
        name = input("(Escribe exit para salir)\nNombre de usuario ya existente. Introduce otro: ")
    if (name == "exit"):
        return
    password = input("Introduzca la contraseña: ") # TODO: CIFRAR CONTRASEÑA
    db.register_new_user(name.lower(), password)

def login_user():
    db = DataBase()
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

    def functionality(self):
            userchoice = input(" 1: AÑADIR ASIGNATURA. \n 2: AÑADIR EXAMEN. \n 3: AÑADIR PROYECTO. \n 4: EXIT \n")
            match userchoice:
                case "1":
                    self.add_subject()
                    return 1
                case "2":
                    self.add_exam()
                    return 1
                case "3":
                    self.add_project()
                    return 1
                case "4":
                    return 0
                case _:
                    print("Error: Acción no válidad")

    def add_subject(self):
        db = DataBase()
        new_subject = input("Escriba asignatura a añadir: ").lower()
        if db.search_subject(self.user_name, new_subject):
            print("Asignatura ya existente!")
            return
        print("Registrar asignatura")
        db.register_new_subject(self.user_name, new_subject)


    def add_exam(self):
        db = DataBase()
        subjects_list = db.subjects_from_user(self.user_name)
        print("Asignaturas disponibles:",subjects_list)
        subject = input("Elije asignatura:")
        while subject not in subjects_list and subject != "0":
            subject = input("No existe la asignatura, elige una asignatura válida. Exit:0 \n")
        if subject == "0":
            return

        exams_lists = db.exams_from_subject(self.user_name, subject)
        print(exams_lists)
        fecha = input("Añada el día del examen [dd-mm-yyyy]") # TODO: REGEX TO VALIDATE DATE

        if fecha in exams_lists:
            print("Ese examen ya está registrado!!")
        else:
            add_mark = input("Quieres añadir una nota al examen?[Y/N]")
            if add_mark == "Y":
                try:
                    mark = int(input("Nota del examen: "))
                except:
                    mark = -1
                    print("Nota no válida, no se asignará nota")
            db.register_new_event(self.user_name, subject, fecha, "EXAM", mark)

    def add_project(self):
        db = DataBase()
        subjects_list = db.subjects_from_user(self.user_name)
        print("Asignaturas disponibles:", subjects_list)
        subject = input("Elije asignatura:")
        while subject not in subjects_list and subject != "0":
            subject = input("No existe la asignatura, elige una asignatura válida. Exit:0 \n")
        if subject == "0":
            return

        project_list = db.projects_from_subject(self.user_name, subject)
        print(project_list)
        fecha = input("Añada la fecha de entrega del proyecto [dd-mm-yyyy]")  # TODO: REGEX TO VALIDATE DATE

        if fecha in project_list:
            print("Ese proyecto ya está registrado!!")
        else:
            add_mark = input("Quieres añadir nota al proyecto?[Y/N]")
            if add_mark == "Y":
                try:
                    mark = int(input("Nota del proyecto: "))
                except:
                    mark = -1
                    print("Nota no válida, no se asignará nota")
            db.register_new_event(self.user_name, subject, fecha, "PROJECT", mark)

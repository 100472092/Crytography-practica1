"""this class encapsules user funtionality"""
from data_base_gestor import DataBase

def register_user():
    db = DataBase()
    name = input("(Escribe exit para salir)\nIntroduzca el nombre de usuario: ")
    while name != "exit" and db.search_user(name.lower()):
        name = input("(Escribe exit para salir)\nNombre de usuario ya existente. Introduce otro: ")
    if name == "exit":
        return
    password = input("Introduzca la contraseña: ") # TODO: CIFRAR CONTRASEÑA
    db.register_new_user(name.lower(), password)

def login_user():
    db = DataBase()
    tries = 3
    fallo = False

    name = input("(Escribe exit para salir)\nIntroduzca el nombre de usuario: ").lower()
    while name != "exit" and db.search_user(name) is None:
        name = input("(Escribe exit para salir)\nNombre de usuario no existe, introduzca un usuario válido.").lower()
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
            user_choice = input(" 1: GESTIONAR ASIGNATURAS. \n 2: GESTIONAR EXAMENES. \n 3: GESTIONAR PROYECTOS. \n 4: EXIT \n")
            match user_choice:
                case "1":
                    self.manage_subject()
                    return 1
                case "2":
                    self.manage_exams()
                    return 1
                case "3":
                    self.manage_projects()
                    return 1
                case "4":
                    return 0
                case _:
                    print("Error: Acción no válidad")

    def manage_subject(self):
        exit_v = False
        while not exit_v:
            user_choice = input(" 1: AÑADIR ASIGNATURA.\n 2: ELIMINAR ASIGNATURA\n 3: EXIT")
            match user_choice:
                case "1":
                    self.add_subject()
                    return
                case "2":
                    print("Si borras una asignatura se borrarán todos los exámenes/proyectos asociados a ella")
                    sure = input("Quieres continuar?[Y/N]: ")
                    if sure == "Y":
                        self.drop_subject()
                    return
                case "3":
                    exit_v = True
                case _:
                    print("Acción no validad")

    def add_subject(self):
        db = DataBase()
        new_subject = input("Escriba asignatura a añadir: ").lower()
        # TODO: Añadir salida
        if db.search_subject(self.user_name, new_subject):
            print("Asignatura ya existente!")
            return
        print("Registrar asignatura")
        db.register_new_subject(self.user_name, new_subject.lower())

    def drop_subject(self):
        db = DataBase()
        exists = False
        subjects_list = db.subjects_from_user(self.user_name)
        while not exists:
            print("Asignaturas: ", subjects_list)
            subj_to_erase = input("Asignatura que desea eliminar: ")
            if subj_to_erase.lower() in subjects_list:
                exists = True
            else:
                print("Esa asignatura no existe")

        db.delete_subject_from_user(self.user_name, subj_to_erase)

    def manage_exams(self):
        db = DataBase()
        subjects_list = db.subjects_from_user(self.user_name)
        print("Asignaturas disponibles:", subjects_list)
        subject = input("Elije asignatura:")
        while subject not in subjects_list and subject != "0":
            subject = input("No existe la asignatura, elige una asignatura válida. Exit:0 \n")
        if subject == "0":
            return

        print("TUS EXAMENES:", db.exams_from_subject(self.user_name, subject))
        exit_v = False
        while not exit_v:
            user_choice = input(" 1: AÑADIR EXAMEN.\n 2: MODIFICAR FECHA DE EXAMEN\n 3: ELIMINAR EXAMEN\n 4: EXIT\n")
            match user_choice:
                case "1":
                    self.add_exam(subject)
                    return
                case "2":
                    self.modify_exam(subject)
                    return
                case "3":
                    self.drop_exam(subject)
                    return
                case "4":
                    exit_v = True
                case _:
                    print("Acción no valida")

    # TODO: generalizar selección de asignatura y examen

    def add_exam(self, subject: str):
        db = DataBase()
        exams_lists = db.exams_from_subject(self.user_name, subject)
        print(exams_lists)
        fecha = input("Añada el día del examen [dd-mm-yyyy]") # TODO: REGEX TO VALIDATE DATE

        if fecha in exams_lists:
            print("Ese examen ya está registrado!!")
        else:
            add_mark = input("Quieres añadir una nota al examen?[Y/N]")
            mark = -1
            if add_mark == "Y":
                try:
                    mark = int(input("Nota del examen: "))
                except:
                    mark = -1
                    print("Nota no válida, no se asignará nota")
            db.register_new_event(self.user_name, subject, fecha, "EXAM", mark)

    def modify_exam(self, subject: str):
        db = DataBase()
        selected = False
        exams_lits = db.exams_from_subject(self.user_name, subject)
        while not selected:
            print(exams_lits)
            old_date = input("Selecciona un examen: ")
            if old_date in exams_lits:
                selected = True
            else:
                print("No existe ese examen")

        new_date = input("nueva fecha")
        db.delete_event(self.user_name, subject, old_date, 'EXAM')
        db.register_new_event(self.user_name, subject, new_date,'EXAM', -1)

    def drop_exam(self, subject: str):
        db = DataBase()
        selected = False
        exams_lits = db.exams_from_subject(self.user_name, subject)
        while not selected:
            print(exams_lits)
            old_date = input("Selecciona un examen: ")
            if old_date in exams_lits:
                selected = True
            else:
                print("No existe ese examen")

        db.delete_event(self.user_name, subject, old_date, 'EXAM')

    def manage_projects(self):
        db = DataBase()
        subjects_list = db.subjects_from_user(self.user_name)
        print("Asignaturas disponibles:", subjects_list)
        subject = input("Elije asignatura:")
        while subject not in subjects_list and subject != "0":
            subject = input("No existe la asignatura, elige una asignatura válida. Exit:0 \n")
        if subject == "0":
            return
        print("TUS PROYECTOS:", db.projects_from_subject(self.user_name, subject))
        exit_v = False
        while not exit_v:
            user_choice = input(" 1: AÑADIR PROYECTO.\n 2: MODIFICAR FECHA DE ENTREGA\n 3: ELIMINAR PROYECTO\n 4: EXIT\n")
            match user_choice:
                case "1":
                    self.add_project(subject)
                    return
                case "2":
                    self.modify_project(subject)
                    return
                case "3":
                    self.drop_project(subject)
                    return
                case "4":
                    exit_v = True
                case _:
                    print("Acción no valida")

    def add_project(self, subject):
        db = DataBase()

        project_list = db.projects_from_subject(self.user_name, subject)
        print(project_list)
        fecha = input("Añada la fecha de entrega del proyecto [dd-mm-yyyy]")  # TODO: REGEX TO VALIDATE DATE

        if fecha in project_list:
            print("Ese proyecto ya está registrado!!")
        else:
            add_mark = input("Quieres añadir nota al proyecto?[Y/N]")
            mark = -1
            if add_mark == "Y":
                try:
                    mark = int(input("Nota del proyecto: "))
                except:
                    mark = -1
                    print("Nota no válida, no se asignará nota")
            db.register_new_event(self.user_name, subject, fecha, "PROJECT", mark)

    def modify_project(self, subject: str):
        db = DataBase()
        selected = False
        project_list = db.projects_from_subject(self.user_name, subject)
        while not selected:
            print(project_list)
            old_date = input("Selecciona un proyecto: ")
            if old_date in project_list:
                selected = True
            else:
                print("No existe ese proyecto")

        new_date = input("nueva fecha")
        db.delete_event(self.user_name, subject, old_date, 'PROJECT')
        db.register_new_event(self.user_name, subject, new_date,'PROJECT', -1)
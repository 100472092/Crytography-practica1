"""this class encapsules user funtionality"""
from data_base_gestor import DataBase


class MyDict:
    def __init__(self, data):
        self.data: dict = data

    def __str__(self):
        out = ""
        for i in self.data:
            exams_i = self.data[i]
            if len(exams_i) < 1:
                exams_i = "sin examenes registrados..."
            out += i + ": " + str(exams_i) + "\n"
        print(out)
        return out

def register_user(user_name: str, password: str):
    db = DataBase()

    if user_name == "" or db.search_user(user_name.lower()) or password == "":
        print("bad name")
        return
    # TODO: CIFRAR CONTRASEÑA
    db.register_new_user(user_name.lower(), password)
    return True

def login_user(user_name: str, pw: str):
    db = DataBase() # TODO: cifrar contraseña
    if db.search_user(user_name) and db.search_pw(pw):
        print("usuario encontrado")
        return User(user_name)
    print("usuario no encontrado")
    return None

class User():
    def __init__(self, user_name):
        self.user_name = user_name

    @property
    def exams(self):
        db = DataBase()
        dict_out = dict()
        for i in db.subjects_from_user(self.user_name):
            dict_out[i] = db.exams_from_subject(self.user_name, i)
        print(dict_out)
        return MyDict(dict_out)

    @property
    def projects(self):
        db = DataBase()
        dict_out = dict()
        for i in db.subjects_from_user(self.user_name):
            dict_out[i] = db.projects_from_subject(self.user_name, i)
        print(dict_out)
        return MyDict(dict_out)

    @property
    def subjects(self):
        db = DataBase()
        out = db.subjects_from_user(self.user_name)
        print(out)
        return out

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

    def add_exam(self, subject: str, date: str, nota: int = -1):
        db = DataBase()
        exams_lists = db.exams_from_subject(self.user_name, subject)
        # TODO: REGEX TO VALIDATE DATE

        if date in exams_lists:
            print("Ese examen ya está registrado!!")
            return False
        else:
            db.register_new_event(self.user_name, subject, date, "EXAM", nota)
            return True

    def modify_exam(self, subject: str, old_date: str, new_subject, new_date, mark):
        db = DataBase()
        if subject not in self.subjects or old_date not in self.exams.data[subject]:
            return False
        db.delete_event(self.user_name, subject, old_date, 'EXAM')
        db.register_new_event(self.user_name, new_subject, new_date, 'EXAM', mark)
        return True

    def drop_exam(self, subject: str, date):
        db = DataBase()
        exams_lits = db.exams_from_subject(self.user_name, subject)
        if date not in exams_lits:
            return False
        db.delete_event(self.user_name, subject, date, 'EXAM')
        return True
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

if __name__ == "__main__":
    print("user")
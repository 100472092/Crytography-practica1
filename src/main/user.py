"""this class encapsules user funtionality"""
from data_base_gestor import DataBase


class MyDict:
    def __init__(self, data, tipo):
        self.data: dict = data
        self.tipo = tipo

    def __str__(self):
        out = ""
        for i in self.data:
            exams_i = self.data[i]
            if len(exams_i) < 1:
                exams_i = "sin " + self.tipo + " registrados..."
            out += i + ": " + str(exams_i) + "\n"
        return out

    def list(self):
        return self.data.items()


def register_user(user_name: str, password: str):
    db = DataBase()

    if user_name == "" or db.search_user(user_name.lower()) or password == "":
        print("Register_user: No se pudo registrar al usuario (bad_name)")
        return
    # TODO: CIFRAR CONTRASEÑA
    db.register_new_user(user_name.lower(), password)
    return True


def login_user(user_name: str, pw: str):
    db = DataBase()  # TODO: cifrar contraseña
    if db.search_user(user_name) and db.search_pw(pw):
        print("log_in: Usuario encontrado")
        return User(user_name)
    print("log_in: Usuario no encontrado")
    return None


class User:
    def __init__(self, user_name):
        self.user_name = user_name

    @property
    def exams(self):
        db = DataBase()
        dict_out = dict()
        for i in db.subjects_from_user(self.user_name):
            dict_out[i] = db.exams_from_subject(self.user_name, i)
        return MyDict(dict_out, "exámenes")

    @property
    def projects(self):
        db = DataBase()
        dict_out = dict()
        for i in db.subjects_from_user(self.user_name):
            dict_out[i] = db.projects_from_subject(self.user_name, i)
        return MyDict(dict_out, "proyectos")

    @property
    def subjects(self):
        db = DataBase()
        out = db.subjects_from_user(self.user_name)
        return out

    def add_subject(self, new_subject):
        db = DataBase()
        new_subject = new_subject.lower()
        # TODO: Añadir salida
        if db.search_subject(self.user_name, new_subject):
            print("ADD_SUBJECT: Asignatura ya existente!")
            return False
        print("ADD_SUBJECT: asignatura añadida")
        db.register_new_subject(self.user_name, new_subject.lower())
        return True

    def drop_subject(self, subject):
        db = DataBase()
        subjects_list = db.subjects_from_user(self.user_name)
        if not subject.lower() in subjects_list:
            print("DROP_SUBJECT: ASIGNATURA NO EXISTE!!")
            return False
        print("DROP_SUBJECT: ASIGNATURA ELIMINADA")
        db.delete_subject_from_user(self.user_name, subject)
        return True

    # TODO: generalizar selección de asignatura y examen

    def add_exam(self, subject: str, date: str, nota: int = -1):
        db = DataBase()
        exams_lists = db.exams_from_subject(self.user_name, subject)
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

    def check_event_mark(self, subject: str, date: str, tipo: str):
        db = DataBase()
        if tipo == 'EXAM':
            valid = (subject not in self.subjects or date not in self.exams.data[subject])
        elif tipo == 'PROJECT':
            valid = (subject not in self.subjects or date not in self.projects.data[subject])
        else:
            print("FATAL ERROR: CHECK_EVENT_MARK")
            return False
        if valid:
            print("Error: No existe el " + tipo + " especificado")
            return False
        return db.search_event(self.user_name, subject, date, tipo).pop()[-1]

    def drop_exam(self, subject: str, date):
        db = DataBase()
        exams_lits = db.exams_from_subject(self.user_name, subject)
        if date not in exams_lits:
            return False
        db.delete_event(self.user_name, subject, date, 'EXAM')
        return True

    def add_project(self, subject, fecha, mark):
        db = DataBase()
        project_list = db.projects_from_subject(self.user_name, subject)
        if fecha in project_list:
            print("Ese proyecto ya está registrado!!")
            return False
        else:
            db.register_new_event(self.user_name, subject, fecha, "PROJECT", mark)
            return True

    def modify_project(self, subject: str, old_date, new_subject, new_date, mark):
        db = DataBase()
        if subject not in self.subjects or old_date not in self.projects.data[subject]:
            return False
        db.delete_event(self.user_name, subject, old_date, 'PROJECT')
        db.register_new_event(self.user_name, new_subject, new_date, 'PROJECT', mark)
        return True

    def drop_project(self, subject: str, date):
        db = DataBase()
        project_list = db.projects_from_subject(self.user_name, subject)
        if date not in project_list:
            return False
        print("DROP_PROJECT: projecto eliminado")
        db.delete_event(self.user_name, subject, date, 'PROJECT')
        return True

    def str_subjects(self):
        out = ""
        for s in self.subjects:
            out += s + ": " + str(len(self.exams.data[s])) + " examene(s) y " + str(
                len(self.projects.data[s])) + " proyecto(s)\n"
        return out


if __name__ == '__main__':
    pass

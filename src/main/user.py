"""this class encapsules user funtionality"""
from data_base_gestor import DataBase
import cifrado
import base64


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


def register_user(user_name: str, password: str, universidad: str, edad: str):
    db = DataBase()

    if user_name == "" or db.search_user(user_name.lower()) or password == "":
        print("Register_user: No se pudo registrar al usuario (bad_name)")
        return
    pw_token, salt_password = cifrado.hash_password(password)
    derived_salt = cifrado.generar_salt()
    derived_key = cifrado.derivar_key(password, derived_salt)
    universidad = cifrado.cifrado_autenticado(universidad, derived_key)
    edad = cifrado.cifrado_autenticado(edad, derived_key)
    db.register_new_user(user_name.lower(), pw_token, salt_password, derived_salt, universidad, edad)
    return True


def login_user(user_name: str, pw: str):
    db = DataBase()
    user_data = db.extract_user_creds(user_name)
    if user_data:
        print("log_in: Usuario encontrado")
        if cifrado.verify_pw(pw, user_data[1], user_data[2]):
            new_token, new_salt = cifrado.hash_password(pw)
            db.update_user_creds(user_name, new_token, new_salt)
            return User(user_name, cifrado.derivar_key(pw, user_data[3]))
    print("log_in: Usuario no encontrado")
    return None


class User:
    def __init__(self, user_name, key):
        self.user_name = user_name
        self.key = key

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
            nota, nonce_nota = cifrado.cifrado_autenticado(str(nota), self.key)
            db.register_new_event(self.user_name, subject, date, "EXAM", nota, nonce_nota)
            return True

    def modify_exam(self, subject: str, old_date: str, new_subject, new_date, mark):
        db = DataBase()
        if subject not in self.subjects or old_date not in self.exams.data[subject]:
            return False
        db.delete_event(self.user_name, subject, old_date, 'EXAM')
        mark, nonce_mark = cifrado.cifrado_autenticado(str(mark), self.key)
        db.register_new_event(self.user_name, new_subject, new_date, 'EXAM', mark, nonce_mark)
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
        event = db.search_event(self.user_name, subject, date, tipo).pop()
        nota, nonce_nota = event[-2], event[-1]
        nota = cifrado.descifrado_autenticado(self.key, nonce_nota, nota)
        return int(nota)

    def drop_exam(self, subject: str, date):
        db = DataBase()
        exams_lits = db.exams_from_subject(self.user_name, subject)
        if date not in exams_lits:
            return False
        db.delete_event(self.user_name, subject, date, 'EXAM')
        return True

    def add_project(self, subject, date, mark):
        db = DataBase()
        project_list = db.projects_from_subject(self.user_name, subject)
        if date in project_list:
            print("Ese proyecto ya está registrado!!")
            return False
        else:
            mark, nonce_mark = cifrado.cifrado_autenticado(str(mark), self.key)
            db.register_new_event(self.user_name, subject, date, "PROJECT", mark, nonce_mark)
            return True

    def modify_project(self, subject: str, old_date, new_subject, new_date, mark):
        db = DataBase()
        if subject not in self.subjects or old_date not in self.projects.data[subject]:
            return False
        db.delete_event(self.user_name, subject, old_date, 'PROJECT')
        mark, nonce_mark = cifrado.cifrado_autenticado(str(mark), self.key)
        db.register_new_event(self.user_name, new_subject, new_date, 'PROJECT', mark, nonce_mark)
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

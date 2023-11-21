"""this class encapsules user funtionality"""
from data_base_gestor import DataBase
import cifrado
import os
import firma

import shutil


UTF8 = 'utf-8'
PATH = os.path.dirname(__file__)[:-8]


def register_user(user_name: str, password: str, universidad: str, edad: str):
    db = DataBase()

    if user_name == "" or db.search_user(user_name.lower()) or password == "":
        print("Register_user: No se pudo registrar al usuario (bad_name)")
        return
    pw_token, salt_password = cifrado.hash_password(password)
    derived_salt = cifrado.generar_salt()
    derived_key = cifrado.derivar_key(password, derived_salt)
    universidad, nonce_universidad = cifrado.cifrado_autenticado(universidad, derived_key)
    edad, nonce_edad = cifrado.cifrado_autenticado(edad, derived_key)
    db.register_new_user(user_name.lower(), pw_token, salt_password, derived_salt, universidad, nonce_universidad, edad, nonce_edad)
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
        return MyDict(dict_out, "EXAM")

    @property
    def projects(self):
        db = DataBase()
        dict_out = dict()
        for i in db.subjects_from_user(self.user_name):
            dict_out[i] = db.projects_from_subject(self.user_name, i)
        return MyDict(dict_out, "PROJECT")

    @property
    def subjects(self):
        db = DataBase()
        out = db.subjects_from_user(self.user_name)
        return out

    def __gen_marks_cerf_str(self, user_name, user_data, subjects, exams, projects):
        user = "Nombre: " + user_name + "\nEdad: " + user_data[2] + "\nUniversidad: " + user_data[1] + "\n"
        separador = "----------------------\n"
        marks = "Asignaturas: " + subjects + "\n" + "Exámenes:\n" + exams + "\nProyectos:\n" + projects + "\n"
        return user + separador + marks

    def get_user_data(self):
        db = DataBase()
        data = db.get_user_data(self.user_name)
        universidad = cifrado.descifrado_autenticado(self.key, data[2], data[1])
        edad = cifrado.descifrado_autenticado(self.key, data[4], data[3])
        return self.user_name, universidad, edad

    def add_subject(self, new_subject):
        db = DataBase()
        new_subject = new_subject.lower()
        if db.search_subject(self.user_name, new_subject):
            print("add_subject: Asignatura ya existente!")
            return False
        print("add_subject: asignatura añadida")
        db.register_new_subject(self.user_name, new_subject.lower())
        return True

    def drop_subject(self, subject):
        db = DataBase()
        subjects_list = db.subjects_from_user(self.user_name)
        if not subject.lower() in subjects_list:
            print("drop_subject: ASIGNATURA NO EXISTE!!")
            return False
        print("drop_subject: ASIGNATURA ELIMINADA")
        db.delete_subject_from_user(self.user_name, subject)
        return True

    def add_exam(self, subject: str, date: str, nota: int = -1):
        db = DataBase()
        exams_lists = db.exams_from_subject(self.user_name, subject)
        if date in exams_lists:
            print("add_exam: ese examen ya está registrado")
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
            print("ERROR: no existe la asignatura" + subject + "especificada")
            return False
        if valid:
            print("ERROR: No existe el " + tipo + " especificado")
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
            print("add_project: ese projecto ya está registrado")
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
        print("drop_project: proyecto eliminado")
        db.delete_event(self.user_name, subject, date, 'PROJECT')
        return True

    def str_subjects(self):
        out = ""
        for s in self.subjects:
            out += s + ": " + str(len(self.exams.data[s])) + " examene(s) y " + str(
                len(self.projects.data[s])) + " proyecto(s)\n"
        return out

    def gen_data(self):
        print("Generando fichero...")
        if not os.path.exists(os.path.dirname(__file__)[:-4] + "/" + self.user_name + "_datos"):
            print("Creando directorio...")
            os.makedirs(os.path.dirname(__file__)[:-4] + "/" + self.user_name + "_datos/", mode=0o777, exist_ok=True)
        cerf_name = os.path.dirname(__file__)[:-4] + "/" + self.user_name + "_datos/" + self.user_name + "_notas.txt"
        subjects = self.subjects
        examns = self.exams
        projects = self.projects
        user_data = self.get_user_data()

        data = self.__gen_marks_cerf_str(self.user_name, user_data, subjects.__str__(), examns.str_marks(self), projects.str_marks(self))

        file = os.open(cerf_name, os.O_CREAT | os.O_RDWR | os.O_TRUNC)
        os.write(file, bytes(data, UTF8))
        os.close(file)

        firma.firmar_fichero(cerf_name)
        shutil.copy(PATH + "OpenSSL/AC1/ac1cert.pem", os.path.dirname(__file__)[:-4] + "/" + self.user_name + "_datos/")
        shutil.copy(PATH + "OpenSSL/A/Acert.pem", os.path.dirname(__file__)[:-4] + "/" + self.user_name + "_datos/")

        # verificacion.verify_all(cerf_name, cerf_name[:-4] + ".sig")


class MyDict:
    def __init__(self, data, tipo):
        self.data: dict = data
        self.tipo = tipo

    def __str__(self):
        out = ""
        for i in self.data:
            exams_i = self.data[i]
            if len(exams_i) < 1:
                if self.tipo == "EXAM":
                    event = "exámenes"
                else:
                    event = "proyectos"
                exams_i = "sin " + event + " registrados..."
            out += i + ": " + str(exams_i) + "\n"
        return out
    def str_marks(self, user: User):
        out = ""
        for i in self.data:
            exams_i = self.data[i]
            out += "\t" + i + ": "
            if len(exams_i) < 1:
                if self.tipo == "EXAM":
                    event = "exámenes"
                else:
                    event = "proyectos"
                out += "sin " + event + " registrados..."
            for j in exams_i:
                mark = user.check_event_mark(i, j, self.tipo)
                if mark < 0:
                    mark = "sin nota registrada"
                out += "\n\t\t" + j + ": " + str(mark)
            out += "\n"
        return out

if __name__ == '__main__':
    pass

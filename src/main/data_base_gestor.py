import os
import sqlite3 as sl
import sql_scripts

PATH = os.path.dirname(__file__)[:-4] + "storage/database.db"


class DataBase:
    """Interfaz con la base de datos. Sólo instanciable una vez"""

    instance = None

    def __new__(cls):
        if not DataBase.instance:
            DataBase.instance = DataBase.__DataBase()
        return DataBase.instance

    def __getattr__(self, item):
        return getattr(self.instance, item)

    def __setattr__(self, key, value):
        return setattr(self.instance, key, value)

    class __DataBase:
        def __init__(self):
            self.path: str = PATH
            self.base = None

        def open(self):
            self.base = sl.connect(PATH)

        def close(self):
            self.base.close()
            self.base = None

        def restore(self):
            """deletes all data"""
            self.drop_base()
            self.initialize()

        def drop_base(self):
            self.open()
            # restauración de la base de datos
            self.base.executescript(
                sql_scripts.DROP_TABLES
            )
            self.close()

        def initialize(self):
            self.open()
            print("Inicializando base de datos...")
            # inicializar
            self.base.executescript(
                sql_scripts.CREATE_TABLES
            )
            self.close()

        def search_user(self, user: str):
            """busca en las credenciales un usuario y, si existe, devuelve el nombre"""
            self.open()
            sql = "SELECT USER_NAME FROM USER_CREDS WHERE USER_NAME=?"
            data = self.base.execute(sql, (user,))
            data = data.fetchall()
            self.close()
            if len(data) >= 1:
                return user
            return None

        def extract_user_creds(self, user_name: str):
            """Busca un password token en las credenciales y, si coincide con uno dado, devuelve true"""
            self.open()
            sql = "SELECT * FROM USER_CREDS WHERE USER_NAME=?"
            data = self.base.execute(sql, (user_name,))
            data = data.fetchall()
            self.close()
            if len(data) == 0:
                return None
            return data[0]

        def update_user_creds(self, user_name: str, new_token: str, new_salt:str):
            self.open()
            sql = "UPDATE USER_CREDS SET PASSWORD=?, SALT_PW=? WHERE USER_NAME=?"
            self.base.execute(sql, (new_token, new_salt, user_name))
            self.base.commit()
            self.close()

        def search_subject(self, user: str, subject: str):
            """busca una asignatura para un usuario, si existe, la devuelve"""
            self.open()
            sql = "SELECT SUBJECT FROM USER_SUBJ WHERE USER_NAME=? AND SUBJECT=?"
            data = self.base.execute(sql, (user, subject))
            data = data.fetchall()
            if len(data) >= 1:
                return subject
            return None

        def search_event(self, user_name: str, subject, date: str, tipo: str):
            self.open()
            sql = "SELECT * FROM USER_EVENT WHERE USER_NAME=? AND SUBJECT=? AND FECHA=? AND TIPO=?"
            data = self.base.execute(sql, (user_name, subject, date, tipo))
            data = data.fetchall()
            return data

        def get_user_data(self, user_name: str):
            self.open()
            sql = "SELECT USER_NAME, UNIVERSIDAD, NONCE_UNIVERSIDAD, EDAD, NONCE_EDAD FROM USER_CREDS WHERE USER_NAME=?"
            data = self.base.execute(sql, (user_name,))
            data = data.fetchall()
            return data[0]

        def register_new_user(self, user: str, password_token: str, salt_pw: str, salt_key: str, universidad: str, nonce_universidad: str, edad: str, nonce_edad: str):
            """annade un nuevo usuario a la base de datos"""
            self.open()
            sql = "INSERT INTO USER_CREDS (USER_NAME, PASSWORD, SALT_PW, SALT_KEY, UNIVERSIDAD, NONCE_UNIVERSIDAD, EDAD, NONCE_EDAD) VALUES(?, ?, ?, ?, ?, ?, ?, ?)"
            self.base.execute(sql, (user, password_token, salt_pw, salt_key, universidad, nonce_universidad, edad, nonce_edad))
            self.base.commit()
            self.close()

        def register_new_subject(self, user: str, new_subject: str):
            """annade una nueva asignatura para un usuario en la base de datos"""
            self.open()
            sql = "INSERT INTO USER_SUBJ (USER_NAME, SUBJECT) VALUES(?, ?)"
            self.base.execute(sql, (user, new_subject))
            self.base.commit()
            self.close()

        def register_new_event(self, user: str, subject: str, fecha: str, tipo: str, nota: str, nonce_nota: str):
            """annade un nuevo evento (exam/project) a la base de datos"""
            self.open()
            sql = "INSERT INTO USER_EVENT (USER_NAME, SUBJECT, FECHA, TIPO, NOTA, NONCE_NOTA) VALUES(?, ?, ?, ?, ?, ?)"
            self.base.execute(sql, (user, subject, fecha, tipo, nota, nonce_nota))
            self.base.commit()
            self.close()

        def delete_subject_from_user(self, user_name: str, subj_to_erase: str):
            self.open()
            sql = ("DELETE FROM USER_EVENT WHERE USER_NAME=? AND SUBJECT=?",
                   "DELETE FROM USER_SUBJ WHERE USER_NAME=? AND SUBJECT=?")
            for i in range(len(sql)):
                self.base.execute(sql[i], (user_name, subj_to_erase))
            self.base.commit()
            self.close()

        def delete_event(self, user_name: str, subject: str, date: str, tipo: str):
            self.open()
            sql = "DELETE FROM USER_EVENT WHERE USER_NAME=? AND SUBJECT=? AND FECHA=? AND TIPO=?"
            self.base.execute(sql, (user_name, subject, date, tipo))
            self.base.commit()
            self.close()

        def exams_from_subject(self, user: str, subject: str):
            """extrae una lista de todos los examens de un usuario dada una asignatura"""
            self.open()
            sql = "SELECT FECHA FROM USER_EVENT WHERE USER_NAME=? AND SUBJECT=? AND TIPO='EXAM'"
            data = self.base.execute(sql, (user, subject)).fetchall()
            out = []
            for item in data:
                out.append(item[0])
            return out

        def projects_from_subject(self, user: str, subject: str):
            """extrae una lista de todos los proyectos de un usuario dada una asignatura"""
            self.open()
            sql = "SELECT FECHA FROM USER_EVENT WHERE USER_NAME=? AND SUBJECT=? AND TIPO='PROJECT'"
            data = self.base.execute(sql, (user, subject)).fetchall()
            out = []
            for item in data:
                out.append(item[0])
            return out

        def subjects_from_user(self, user: str):
            """extrae una lista de todas las asignaturas de un usuario"""
            self.open()
            sql = "SELECT SUBJECT FROM USER_SUBJ WHERE USER_NAME=?"
            data = self.base.execute(sql, (user,)).fetchall()
            out = []
            for i in range(len(data)):
                out.append(data[i][0])
            return out

        # MÉTODOS DE DEBUG Y TEST
        def insert_test_case(self):
            self.open()
            data = [
                ("pepe", "1234", "0"),
                ("juan", "1234", "0"),
                ("sabrina", "1234", "0"),
            ]
            self.base.executemany("INSERT INTO USER_CREDS (USER_NAME, PASSWORD, SALT_PW) VALUES(?, ?, ?)", data)
            data = [
                ("pepe", "matematicas"),
                ("pepe", "lengua"),
                ("pepe", "naturales"),
                ("pepe", "sociales"),
                ("pepe", "ingles"),
                ("pepe", "religion"),

                ("juan", "filosofia")
            ]
            self.base.executemany("INSERT INTO USER_SUBJ (USER_NAME, SUBJECT) VALUES(?, ?)", data)
            data = [
                ("pepe", "matematicas", "2012-01-01", "EXAM", 9),
                ("pepe", "lengua", "2013-12-12", "EXAM", 8),
                ("pepe", "lengua", "2014-12-12", "EXAM", 8),
                ("pepe", "lengua", "2015-12-12", "EXAM", 8),
                ("pepe", "ingles", "2014-12-12", "EXAM", 7),
                ("pepe", "naturales", "2015-12-12", "EXAM", 6),
                ("pepe", "sociales", "2016-12-12", "EXAM", 5),

                ("pepe", "matematicas", "2012-12-12", "PROJECT", 7),
                ("pepe", "lengua", "2012-12-12", "PROJECT", 6),

            ]
            self.base.executemany(
                "INSERT INTO USER_EVENT (USER_NAME, SUBJECT, FECHA, TIPO, NOTA) VALUES(?, ?, ?, ?, ?)", data)
            self.base.commit()
            self.close()

        def print_subj(self):
            self.open()
            data = self.base.execute("select * from USER_SUBJ")
            for r in data:
                print(r)
            self.close()

        def print_creds(self):
            self.open()
            data = self.base.execute("select * from USER_CREDS")
            for r in data:
                print(r)
            self.close()

        def print_events(self):
            self.open()
            data = self.base.execute("select * from USER_EVENT")
            for r in data:
                print(r)
            self.close()

        def print_all(self):
            self.print_creds()
            self.print_subj()
            self.print_events()


if __name__ == "__main__":
    print(PATH)
    db = DataBase()
    db.restore()
    # db.initialize()
    control = input("wanna insert test data?[Y/N]: ")
    if control == "Y":
        db.insert_test_case()

    db.extract_user_creds("pepe")
    db.print_all()

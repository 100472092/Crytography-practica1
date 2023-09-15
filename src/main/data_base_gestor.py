import os
import sqlite3 as sl

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
            self.base: DataBase = None

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
                """
                DROP TABLE USER_CREDS;
                DROP TABLE USER_SUBJ;
                DROP TABLE USER_EVENT;
                """
            )
            self.close()

        def initialize(self):
            self.open()
            print("Inicializando base de datos...")
            # inicializar
            # TODO: mover el scrip de sql a otro archivo e importarlo
            self.base.executescript(
                """
                CREATE TABLE USER_CREDS (
                    USER_NAME TEXT PRIMARY KEY, 
                    PASSWORD TEXT NOT NULL
                );
                
                CREATE TABLE USER_SUBJ (
                    USER_NAME TEXT,
                    SUBJECT TEXT,
                    
                    PRIMARY KEY(USER_NAME, SUBJECT),
                    FOREIGN KEY(USER_NAME) REFERENCES USER_CREDS(USER_NAME)
                );
            
                CREATE TABLE USER_EVENT (
                    USER_NAME TEXT,
                    SUBJECT TEXT,
                    FECHA DATE,
                    TIPO TEXT,
                    NOTA INTEGER,
                    
                    PRIMARY KEY(USER_NAME, SUBJECT, FECHA, TIPO),
                    FOREIGN KEY(USER_NAME, SUBJECT) REFERENCES USER_SUBJ(USER_NAME, SUBJECT)
                );
                """
            )
            self.close()

        def search_user(self, user: str):
            """busca en las credenciales un usuario y, si existe, devuelve el nombre"""
            self.open()
            sql = "SELECT USER_NAME FROM USER_CREDS WHERE USER_NAME=?"
            data = self.base.execute(sql, (user, ))
            data = data.fetchall()
            self.close()
            if len(data) >= 1:
                # print("found")
                return user
            return None

        def search_pw(self, password_tk: str):
            """Busca un password token en las credenciales y, si coincide con uno dado, devuelve true"""
            self.open()
            sql = "SELECT PASSWORD FROM USER_CREDS WHERE PASSWORD=?"
            data = self.base.execute(sql, (password_tk, ))
            data = data.fetchall()
            self.close()
            if len(data) >= 1:
                # print("found")
                return True # no devolvemos el pw_token por seguridad
            return False

        def search_subject(self, user: str, subject: str):
            """busca una asignatura para un usuario, si existe, la devuelve"""
            self.open()
            sql = "SELECT SUBJECT FROM USER_SUBJ WHERE USER_NAME=? AND SUBJECT=?"
            data = self.base.execute(sql, (user, subject))
            data = data.fetchall()
            if len(data) >= 1:
                print("found")
                return subject
            return None

        def register_new_user(self, user: str, password_token: str):
            """annade un nuevo usuario a la base de datos"""
            self.open()
            sql = "INSERT INTO USER_CREDS (USER_NAME, PASSWORD) VALUES(?, ?)"
            self.base.execute(sql, (user, password_token))
            self.base.commit()
            self.close()

        def register_new_subject(self, user: str, new_subject:str):
            """annade una nueva asignatura para un usuario en la base de datos"""
            self.open()
            sql = "INSERT INTO USER_SUBJ (USER_NAME, SUBJECT) VALUES(?, ?)"
            self.base.execute(sql, (user, new_subject))
            self.base.commit()
            self.close()

        def register_new_event(self, user: str, subject: str, fecha: str, tipo: str, nota: int):
            """annade un nuevo evento (exam/project) a la base de datos"""
            self.open()
            sql = "INSERT INTO USER_EVENT (USER_NAME, SUBJECT, FECHA, TIPO, NOTA) VALUES(?, ?, ?, ?, ?)"
            self.base.execute(sql, (user, subject, fecha, tipo, nota))
            self.base.commit()
            self.close()

        def exams_from_subject(self, user:str, subject: str):
            """extrae una lista de todos los examens de un usuario dada una asignatura"""
            self.open()
            sql = "SELECT FECHA FROM USER_EVENT WHERE USER_NAME=? AND SUBJECT=? AND TIPO='EXAM'"
            data = self.base.execute(sql, (user, subject)).fetchall()
            out = []
            for item in data:
                out.append(item[0])
            return out

        def subjects_from_user(self, user:str):
            """extrae una lista de todas las asignaturas de un usuario"""
            self.open()
            sql = "SELECT SUBJECT FROM USER_SUBJ WHERE USER_NAME=?"
            data = self.base.execute(sql, (user, )).fetchall()
            out = []
            for i in range(len(data)):
                out.append(data[i][0])
            return out

        # MÉTODOS DE DEBUG Y TEST
        def insert_test_case(self):
            self.open()
            data = [
                ("pepe", "1234"),
                ("juan", "1234"),
                ("sabrina", "1234"),
            ]
            self.base.executemany("INSERT INTO USER_CREDS (USER_NAME, PASSWORD) VALUES(?, ?)", data)
            data = [
                ("pepe", "matematicas"),
                ("pepe", "lengua"),
                ("juan", "filosofia")
            ]
            self.base.executemany("INSERT INTO USER_SUBJ (USER_NAME, SUBJECT) VALUES(?, ?)", data)
            data = [
                ("pepe", "matematicas", "12-12-2012", "EXAM", 9),
                ("pepe", "lengua", "01-01-2013", "EXAM", 9),
                ("pepe", "lengua", "12-12-2012", "EXAM", 9),
            ]
            self.base.executemany("INSERT INTO USER_EVENT (USER_NAME, SUBJECT, FECHA, TIPO, NOTA) VALUES(?, ?, ?, ?, ?)", data)
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
    control = input("wanna insert test data?[Y/N]: ")
    if control == "Y":
        db.insert_test_case()
    db.print_all()

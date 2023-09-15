import os
import sqlite3 as sl

PATH = os.path.dirname(__file__)[:-4] + "storage/database.db"


class DataBase:
    def __init__(self):
        self.path = PATH
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
            """
            DROP TABLE USER_CREDS;
            DROP TABLE USER_SUBJ;
            DROP TABLE USER_EVENT;
            """
        )
        self.close()

    def initialize(self):
        self.open()
        print("inicializar base de datos...")
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

    def insert_test_case(self):
        self.open()
        data = [
            ("pepe", "1234"),
            ("juan", "1234"),
            ("sabrina", "1234"),
        ]
        self.base.executemany("INSERT INTO USER_CREDS (USER_NAME, PASSWORD) VALUES(?, ?)", data)
        self.base.execute("commit")
        self.close()


    def search_user(self, user: str):
        """looks for a user in creds table and returns its name if exists"""
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
        """looks for a user in creds table and returns its name if exists"""
        self.open()
        sql = "SELECT PASSWORD FROM USER_CREDS WHERE PASSWORD=?"
        data = self.base.execute(sql, (password_tk, ))
        data = data.fetchall()
        self.close()
        if len(data) >= 1:
            # print("found")
            return True
        return False

    def print_creds(self):
        self.open()
        data = self.base.execute("select * from USER_CREDS")
        for r in data:
            print(r)
        self.close()
    def register_new_user(self, user: str, password_token: str):
        self.open()
        sql = "INSERT INTO USER_CREDS (USER_NAME, PASSWORD) VALUES(?, ?)"
        self.base.execute(sql, (user, password_token))
        self.base.execute("commit")
        self.close()
        self.print_creds()

if __name__ == "__main__":
    db = DataBase()
    db.restore()
    control = input("wanna insert test data?[Y/N]: ")
    if (control == "Y"):
        db.insert_test_case()
    db.print_creds()
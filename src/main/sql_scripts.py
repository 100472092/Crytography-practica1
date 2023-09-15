DROP_TABLES = """
                DROP TABLE USER_CREDS;
                DROP TABLE USER_SUBJ;
                DROP TABLE USER_EVENT;
                """

CREATE_TABLES = """
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
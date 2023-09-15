import user
from data_base_gestor import DataBase

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    db = DataBase()
    #db.insert_test_case()
    while True:
        userchoice = input("Presione un número para empezar:\n 1: REGISTRAR NUEVO USUARIO. \n 2: INICIAR SESION. \n 3. SALIR\n")
        if userchoice == "1":
            user.register_user(db)
        elif userchoice == "2":
            valid_user = user.login_user(db)
            if valid_user:
                valid_user.functionality()
        elif userchoice == "3":
            print("Saliendo...")
            break
        else:
            print("ERROR, acción no válida")

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

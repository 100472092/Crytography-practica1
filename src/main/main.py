import user
import os
from data_base_gestor import DataBase

def main():
    # Sino existe, inicializa la base de datos
    if not os.path.exists(os.path.dirname(__file__)[:-4] + "storage"):
        os.makedirs(os.path.dirname(__file__)[:-4] + "storage", mode=0o777, exist_ok=False)
        DataBase().initialize()

    valid_user = None
    while valid_user is None:
        # db = DataBase().print_all() # Debug
        userchoice = input(
            "Presione un número para empezar:\n 1: REGISTRAR NUEVO USUARIO. \n 2: INICIAR SESION. \n 3. SALIR\n")
        if userchoice == "1":
            user.register_user()
        elif userchoice == "2":
            valid_user = user.login_user()
        elif userchoice == "3":
            print("Saliendo...")
            return 0
        else:
            print("ERROR, acción no válida")
    exit_code = 1
    while not exit_code == 0:
        exit_code = valid_user.functionality()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()


# See PyCharm help at https://www.jetbrains.com/help/pycharm/

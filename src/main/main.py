import user
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    while True:
        userchoice = input("Presione un número para empezar:\n 1: REGISTRAR NUEVO USUARIO. \n 2: INICIAR SESION. \n")
        if userchoice == "1":
            user.register_user()
        elif userchoice == "2":
            valid_user = user.login_user()
            if valid_user:
                valid_user.functionality()
        else:
            print("ERROR, acción no válida")

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

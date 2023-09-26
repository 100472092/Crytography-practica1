import os
from data_base_gestor import DataBase
from app import App


def main():
    # Sino existe, inicializa la base de datos
    if not os.path.exists(os.path.dirname(__file__)[:-4] + "storage/database.db"):
        print("Creando base de datos...")
        os.makedirs(os.path.dirname(__file__)[:-4] + "storage", mode=0o777, exist_ok=True)
        DataBase().initialize()

    # funcionalidad de la interfaz gráfica
    App()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

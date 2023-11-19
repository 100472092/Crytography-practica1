import os

import firma
from data_base_gestor import DataBase
from app import App

os.environ["key"] = "$4lCH1tX45"
DIR_PATH = os.path.dirname(__file__)[:-4]

def main():
    # Si no existe, inicializa la base de datos
    if not os.path.exists(DIR_PATH + "storage/database.db"):
        print("Creando base de datos...")
        os.makedirs(DIR_PATH + "storage", mode=0o777, exist_ok=True)
        DataBase().initialize()

    # Si no existen claves para el sistema se generan
    if not os.path.exists(DIR_PATH + "keys/private.pem"):
        print("Generando claves...")
        os.makedirs(DIR_PATH + "keys", mode=0o777, exist_ok=True)
        firma.generar_claves(DIR_PATH + "/keys/")
    if not os.path.exists(DIR_PATH + "keys/public.pem"):
        print("Generando clave publica...")
        os.makedirs(DIR_PATH + "keys", mode=0o777, exist_ok=True)
        firma.gen_public(DIR_PATH + "/keys/")

    # funcionalidad de la interfaz gráfica
    App()

if __name__ == '__main__':
    main()


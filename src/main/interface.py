import streamlit as sl
import random


"""class Interface():
    def __init__(self):
        self.state = "login"


    def log_in_menu(self):
        sl.markdown("# Inicia sesión!!")
        sl.text_input(label="Nombre de usuario", key="user_name")
        sl.markdown("### No tienes cuenta?")
        result = sl.button("Registrate")
        sl.write(result)
        self.state = "registro"

    def sign_up_menu(self):
        sl.markdown("# vamos a registrarte")"""


from tkinter import *
from tkinter import ttk
root = Tk()
frm = ttk.Frame(root, padding=500)
frm.grid()
ttk.Label(frm, text="Hello World!").grid(column=0, row=0)
button = ttk.Button(frm, text="Quit", command=root.destroy)
button.grid(column=1, row=1)
ttk.Button(frm, text="Hey", command=button.destroy).grid(column=2, row=0)
root.mainloop()
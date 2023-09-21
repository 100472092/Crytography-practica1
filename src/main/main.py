import user
import os
from data_base_gestor import DataBase
from tkinter import *
from tkinter import ttk
import time

class App():

    curr_user = None
    password_tries = 3
    def __init__(self):
        self.root = Tk()
        self.root.geometry("600x600")
        self.root.title("AGENDA")
        self.root.resizable(width=False, height=False)

        # Marco principal, permite organizar por grid en caso necesario
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill='both')

        # etiqueta accesible por todoslos elementos: comunica mensajes de error
        self.error_stream = Label(self.main_frame, text="", fg="red", font=("arial", 18))
        self.error_stream.pack(side=BOTTOM)

        # Primera escena
        self.log_in_scene(self.main_frame)

        # bucle principal
        self.root.mainloop()


    def error_stream_restore(self):
        self.error_stream.config(text="")

    def log_in_scene(self, root):
        self.error_stream.config(text="")
        main_frame = ttk.Frame(root)

        main_frame.configure(borderwidth=3, relief="groove")
        main_frame.pack(pady=140, ipady=10)
        sub_frame = ttk.Frame(main_frame)
        sub_frame.pack()
        user_name_label = Label(sub_frame, text="Nombre de usuario:")
        user_name_label.grid(row=0, column=0, ipady=10)
        user_name_box = Entry(sub_frame)
        user_name_box.grid(row=1, column=0)
        user_pw_label = Label(sub_frame, text="Contraseña:")
        user_pw_label.grid(row=2, column=0, ipady=10)
        user_pw_box = Entry(sub_frame, show="*")
        user_pw_box.grid(row=3, column=0)
        bad_name = Label(main_frame, text="", fg='red')
        bad_name.pack(side=BOTTOM)
        login_button = Button(main_frame, text="Log in",
                                   command=lambda: self.main_login_user(user_name_box.get(), user_pw_box.get(), bad_name, main_frame))
        login_button.pack(pady=10)
        register_label = Label(main_frame, text="No tienes cuenta?")
        register_label.pack(pady=10)
        register_button = Button(main_frame, text="Registrate!!",
                                 command=lambda: self.change_to_register(main_frame))
        register_button.pack()


    def main_login_user(self, user_name, password, label, frame):
        if self.password_tries > 0:
            self.password_tries -= 1
            if self.password_tries == 0:
                print("warning_message")
                self.error_stream.config(text="Si fallas una vez más,\nla aplicación se bloqueará 30 segundos")
        else:
            print("demasiados intentos:")
            frame.destroy()
            time.sleep(10)
            return
        self.curr_user = user.login_user(user_name, password)
        if not self.curr_user:
            label.config(text="Bad log in")
            return
        self.change_to_user_functionality(frame)

    def change_to_user_functionality(self, frame):
        self.error_stream_restore()
        frame.destroy()
        self.functionality_scene(self.main_frame)

    def functionality_scene(self, root):
        main_frame = ttk.Frame(root)
        main_frame.pack()
        tittle = Label(main_frame, text="Agenda", font=("Ubuntu", 30))
        tittle.grid(row=0, column=0)
        sub_frame = Frame(main_frame, borderwidth=3, relief="groove")
        sub_frame.grid(row=1, column=0)
        subj_button = Button(sub_frame, text="Aignaturas", padx=10)
        subj_button.grid(row=0, column=0)
        exams_button = Button(sub_frame, text="Exams", padx=10)
        exams_button.grid(row=0, column=1)
        project_button = Button(sub_frame, text="Projects", padx=10)
        project_button.grid(row=0, column=2)
        exit_button = Button(sub_frame, text="Salir", command= lambda: self.change_to_log_in(main_frame))
        exit_button.grid(row=1, column=1, pady=50)



    def change_to_register(self, frame):
        self.error_stream_restore()
        frame.destroy()
        self.register_scene(self.main_frame)

    def register_scene(self, root):
        main_frame = ttk.Frame(root)

        main_frame.configure(borderwidth=3, relief="groove")
        main_frame.pack(pady=150, ipady=10)

        user_name_label = Label(main_frame, text="Nombre de usuario:")
        user_name_label.pack()
        user_name_box = Entry(main_frame)
        user_name_box.pack()
        user_pw_label = Label(main_frame, text="Contraseña:")
        user_pw_label.pack()
        user_pw_box = Entry(main_frame, show="*")
        user_pw_box.pack()
        sub_frame = Frame(main_frame)
        sub_frame.pack()
        bad_name = Label(main_frame, text="", fg='red')
        bad_name.pack(side=BOTTOM)
        register_button = Button(sub_frame, text="registrar",
                                 command=lambda: self.main_register_user(user_name_box.get(), user_pw_box.get(),
                                                                         main_frame, root, bad_name))
        register_button.grid(row=0, column=0, pady=10, padx=10)
        exit_button = Button(sub_frame, text="salir",
                             command=lambda: self.change_to_log_in(main_frame))
        exit_button.grid(row=0, column=2, pady=10, padx=10, ipadx=18)



    def change_to_log_in(self, frame):
        frame.destroy()
        self.log_in_scene(self.main_frame)


    def main_register_user(self, user_name, password, frame, root, bad_label):

        if not user.register_user(user_name, password):
            bad_label.config(text="bad name", font=("arial", 12))
            return
        frame.destroy()
        self.log_in_scene(root)



def main():
    # Sino existe, inicializa la base de datos
    if not os.path.exists(os.path.dirname(__file__)[:-4] + "storage"):
        os.makedirs(os.path.dirname(__file__)[:-4] + "storage", mode=0o777, exist_ok=False)
        DataBase().initialize()

    App()






    """exit_code = 1
    while not exit_code == 0:
        exit_code = valid_user.functionality()"""


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()


# See PyCharm help at https://www.jetbrains.com/help/pycharm/

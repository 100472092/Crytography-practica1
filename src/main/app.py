import user
import constantes
from tkinter import *
from tkinter import ttk
import time
import re

TITTLE_SIZE = constantes.TITTLE_SIZE
SUBTITLE_SIZE = constantes.SUBTITLE_SIZE
ERR_MSG_SIZE = constantes.ERR_MSG_SIZE


class App:
    curr_user = None
    password_tries = 3
    allow_mod = False

    def __init__(self):
        self.root = Tk()
        self.root.geometry("900x600")
        self.root.title("AGENDA")
        self.root.resizable(width=False, height=False)

        # Marco principal, se pasa como argumento a todoas las escenas
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill='both')

        # etiqueta accesible por todoslos elementos: comunica mensajes de error
        self.error_stream = Label(self.main_frame, text="", fg="red", font=(constantes.ERR_FONT, ERR_MSG_SIZE))
        self.error_stream.pack(side=BOTTOM, pady=0)

        # Primera escena
        self.log_in_scene(self.main_frame)
        # self.exam_scene(self.main_frame)
        # bucle principal
        self.root.mainloop()

    # == FUNCIONALIDAD ==
    def error_stream_restore(self):
        self.error_stream.config(text="")

    def app_login_user(self, user_name, password, label, frame):
        if self.password_tries > 0:
            self.password_tries -= 1
            if self.password_tries == 0:
                print("warning_message")
                self.error_stream.config(text="Si fallas una vez más\nla aplicación se bloqueará 5 segundos")
        else:
            print("demasiados intentos:")
            frame.destroy()
            time.sleep(5)
            self.log_in_scene(self.main_frame)
            self.password_tries = 3
            return
        self.curr_user = user.login_user(user_name, password)
        if not self.curr_user:
            label.config(text="Bad log in")
            return
        self.change_to_user_functionality(frame)

    def app_register_user(self, user_name, password, frame, root, bad_label):

        if not user.register_user(user_name, password):
            bad_label.config(text="bad name", font=(constantes.ERR_FONT, ERR_MSG_SIZE))
            return
        frame.destroy()
        self.log_in_scene(root)

    def validate_data(self, subject, date, nota=0):
        err_msg = ""
        if not len(subject) > 0 or subject not in self.curr_user.subjects:
            err_msg = "asignatura no válida"
            return False, err_msg
        if not re.match(r"^(2[0-9]{3})(-)(1[0-2]|0[1-9])(-)(3[01]|[12][0-9]|0[1-9])$", date):
            err_msg = "Fecha no válida"
            return False, err_msg
        try:
            if nota == "":
                return True, err_msg
            nota = int(nota)
            if nota < 0:
                err_msg = "La nota debe ser mayor o igual que 0"
                return False, err_msg
        except:
            err_msg = "La nota debe ser un número entero"
            return False, err_msg
        return True, err_msg

    def app_add_exam(self, subject: str, date, nota, channel, exams):
        valid, err_msg = self.validate_data(subject, date, nota)
        # Nota no es campo obligatorio
        if nota == "":
            nota = -1
        if valid and self.curr_user.add_exam(subject, date, nota):
            channel.config(text="Examen añadido", fg='green')
        else:
            channel.config(text=err_msg, fg="red")
        exams.config(text=self.curr_user.exams)

    def app_modify_exam(self, old_subject, old_date, new_subject, new_date, mark, err_channel, exams):
        if self.allow_mod:
            valid, err_msg = self.validate_data(new_subject, new_date, mark)
            if not valid:
                err_channel.config(text=err_msg, fg='red')
                return
            if new_date not in self.curr_user.exams.data[new_subject]:
                if not self.curr_user.modify_exam(old_subject, old_date, new_subject, new_date, mark):
                    print("FATAL ERROR: FALLO EN LA MODIFICACIÓN EN LA BASE DE DATOS")
                    return
                exams.config(text=self.curr_user.exams)
                err_channel.config(text='Examen modificado', fg='green')
            else:
                err_channel.config(text='Ya existe ese examen', fg='red')
        else:
            err_channel.config(text="Selecciona primero un examen", fg='red')

    def app_delete_exam(self, subject, date, channel, exams):
        valid, err_msg = self.validate_data(subject, date)
        if not valid:
            channel.config(text=err_msg, fg='red')
            return
        if date in self.curr_user.exams.data[subject]:
            if not self.curr_user.drop_exam(subject, date):
                print("Fecha que no existe")
            channel.config(text="Examen eliminado", fg='green')
            exams.config(text=self.curr_user.exams)

    # == TRANSICIONES ==
    def change_to_log_in(self, frame):
        frame.destroy()
        self.log_in_scene(self.main_frame)

    def change_to_register(self, frame):
        self.error_stream_restore()
        frame.destroy()
        self.register_scene(self.main_frame)

    def change_to_user_functionality(self, frame):
        self.error_stream_restore()
        frame.destroy()
        self.functionality_scene(self.main_frame)

    def change_to_exam_scene(self, frame):
        self.error_stream_restore()
        frame.destroy()
        self.exam_scene(self.main_frame)

    def change_to_add_exam_scene(self, frame):
        self.error_stream_restore()
        frame.destroy()
        self.add_exam_scene(self.main_frame)

    def change_to_modify_exam_scene(self, frame):
        self.error_stream_restore()
        frame.destroy()
        self.modify_exam_scene(self.main_frame)

    def change_to_delete_exam_scene(self, frame):
        self.error_stream_restore()
        frame.destroy()
        self.delete_exam_scene(self.main_frame)

    # == ESCENAS ==
    def log_in_scene(self, root):
        self.error_stream.config(text="")
        main_frame = ttk.Frame(root)

        main_frame.configure(borderwidth=3, relief="groove")
        main_frame.pack(pady=115, ipady=10)
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
                              command=lambda: self.app_login_user(user_name_box.get(), user_pw_box.get(), bad_name,
                                                                  main_frame))
        login_button.pack(pady=10)
        register_label = Label(main_frame, text="No tienes cuenta?")
        register_label.pack(pady=10)
        register_button = Button(main_frame, text="Registrate!!",
                                 command=lambda: self.change_to_register(main_frame))
        register_button.pack()

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
                                 command=lambda: self.app_register_user(user_name_box.get(), user_pw_box.get(),
                                                                        main_frame, root, bad_name))
        register_button.grid(row=0, column=0, pady=10, padx=10)
        exit_button = Button(sub_frame, text="salir",
                             command=lambda: self.change_to_log_in(main_frame))
        exit_button.grid(row=0, column=2, pady=10, padx=10, ipadx=18)

    def functionality_scene(self, root):
        main_frame = ttk.Frame(root)
        main_frame.pack()
        tittle = Label(main_frame, text="Agenda", font=(constantes.TITTLE_FONT, TITTLE_SIZE))
        tittle.grid(row=0, column=0, ipady=10)
        sub_frame = Frame(main_frame, borderwidth=3, relief="groove")
        sub_frame.grid(row=1, column=0)
        sub_title = Label(sub_frame, text="Qué quiere consultar?", font=(constantes.SUBTITLE_FONT, SUBTITLE_SIZE))
        sub_title.grid(row=0, column=0, columnspan=3, pady=10)
        subj_button = Button(sub_frame, text="Asignaturas")
        subj_button.grid(row=1, column=0)
        exams_button = Button(sub_frame, text="Exams", command=lambda: self.change_to_exam_scene(main_frame))
        exams_button.grid(row=1, column=1, ipadx=20)
        project_button = Button(sub_frame, text="Projects", padx=15)
        project_button.grid(row=1, column=2, ipadx=16)
        exit_button = Button(sub_frame, text="Salir", command=lambda: self.change_to_log_in(main_frame))
        exit_button.grid(row=2, column=1, pady=50)

    def exam_scene(self, frame):
        main_frame = ttk.Frame(frame)
        main_frame.pack()
        tittle = Label(main_frame, text="Gestión de exámenes", font=(constantes.TITTLE_FONT, TITTLE_SIZE))
        tittle.pack(pady=10, fill="x")
        sub_frame = ttk.Frame(main_frame, borderwidth=3, relief="groove")
        sub_frame.pack()
        sub_title = Label(sub_frame, text="Tus exámenes:\t\t", justify=LEFT,
                          font=(constantes.SUBTITLE_FONT, SUBTITLE_SIZE))
        sub_title.pack()
        exam_dict = self.curr_user.exams
        exams = Label(sub_frame, text=exam_dict.__str__(), justify=LEFT)
        exams.pack()
        actions_frame = ttk.Frame(main_frame)
        actions_frame.pack()
        add_button = Button(actions_frame, text="ADD", command=lambda: self.change_to_add_exam_scene(main_frame))
        add_button.grid(row=0, column=0)
        mod_button = Button(actions_frame, text="MODIFY", command=lambda: self.change_to_modify_exam_scene(main_frame))
        mod_button.grid(row=0, column=1)
        del_button = Button(actions_frame, text="DELETE", command=lambda: self.change_to_delete_exam_scene(main_frame))
        del_button.grid(row=0, column=2)
        quit_button = Button(main_frame, text="Back", command=lambda: self.change_to_user_functionality(main_frame))
        quit_button.pack()

    def add_exam_scene(self, root):
        main_frame = Frame(root, borderwidth=constantes.FRAME_BORDERWIDTH, relief="groove")
        main_frame.pack()
        tittle = Label(main_frame, text="Añadir", font=(constantes.TITTLE_FONT, TITTLE_SIZE))
        tittle.grid(row=0, column=0, columnspan=2)
        err_comunication = Label(main_frame, text="", font=(constantes.SUBTITLE_FONT, ERR_MSG_SIZE), pady=10)

        exams_frame = Frame(main_frame, borderwidth=3, relief="groove")
        sub_title = Label(exams_frame, text="Tus exámenes:\t\t", justify=LEFT, font=(SUBTITLE_SIZE, SUBTITLE_SIZE))
        exams = Label(exams_frame, text=self.curr_user.exams.__str__(), justify=LEFT)

        sub_frame = Frame(main_frame, borderwidth=constantes.FRAME_BORDERWIDTH, relief="groove", padx=5, pady=5)
        sub_frame.grid(row=1, column=0, ipady=23)
        subj_label = Label(sub_frame, text="Asignatura*")
        date_label = Label(sub_frame, text="Fecha*")
        mark_label = Label(sub_frame, text="Nota")
        subj_label.grid(row=0, column=0)
        date_label.grid(row=1, column=0)
        mark_label.grid(row=2, column=0)
        subj_box = Entry(sub_frame)
        date_box = Entry(sub_frame)
        mark_box = Entry(sub_frame)
        subj_box.grid(row=0, column=1)
        date_box.grid(row=1, column=1)
        mark_box.grid(row=2, column=1)
        buttons_frame = Frame(sub_frame)
        buttons_frame.grid(row=3, column=0, columnspan=2)
        confirm_button = Button(buttons_frame, text="ADD",
                                command=lambda: self.app_add_exam(subj_box.get(), date_box.get(), mark_box.get(),
                                                                  err_comunication, exams))
        quit_button = Button(buttons_frame, text="QUIT", command=lambda: self.change_to_user_functionality(main_frame))
        confirm_button.pack(side="left", pady=5)
        quit_button.pack(side="right", pady=5)

        err_comunication.grid(row=2, column=0, columnspan=2)
        exams_frame.grid(row=1, column=1)
        sub_title.pack()
        exams.pack()

    def modify_exam_scene(self, root):
        main_frame = Frame(root)
        main_frame.pack()
        tittle = Label(main_frame, text="Modificar", font=(constantes.TITTLE_FONT, TITTLE_SIZE))
        tittle.grid(row=0, column=0, columnspan=2, ipady=10)
        body_frame = Frame(main_frame, borderwidth=constantes.FRAME_BORDERWIDTH, relief="groove")
        body_frame.grid(row=1, column=0)

        exams_frame = Frame(main_frame, borderwidth=3, relief="groove")
        sub_title = Label(exams_frame, text="Tus exámenes:\t\t", justify=LEFT, font=(SUBTITLE_SIZE, SUBTITLE_SIZE))
        exams = Label(exams_frame, text=self.curr_user.exams.__str__(), justify=LEFT)

        select_frame = Frame(body_frame, borderwidth=constantes.FRAME_BORDERWIDTH, relief="groove")
        select_frame.pack(ipady=5)
        err_communication = Label(select_frame, text="", font=(constantes.ERR_FONT, ERR_MSG_SIZE), pady=5)
        select_subj = Entry(select_frame)
        select_date = Entry(select_frame)
        select_subj_label = Label(select_frame, text="Asignatura")
        select_date_label = Label(select_frame, text="Fecha")
        select_label = Label(select_frame, text="Seleccion:")
        apply_button = Button(select_frame, text="Aplicar selección",
                              command=lambda: self.apply_selection(select_subj.get(), select_date.get(),
                                                                   err_communication, old_subj_box, old_date_box,
                                                                   old_mark_box))

        select_label.grid(row=1, column=0)
        select_subj_label.grid(row=0, column=1)
        select_date_label.grid(row=0, column=2)
        select_subj.grid(row=1, column=1)
        select_date.grid(row=1, column=2)
        apply_button.grid(row=2, column=0, columnspan=3, pady=5)
        err_communication.grid(row=3, column=0, columnspan=3)

        change_frame = Frame(body_frame)
        change_frame.pack()
        old_label = Label(change_frame, text="ANTIGUO")
        new_label = Label(change_frame, text="NUEVO")
        old_subj_box = Entry(change_frame, state=DISABLED)
        old_date_box = Entry(change_frame, state=DISABLED)
        old_mark_box = Entry(change_frame, state=DISABLED)
        new_subj_box = Entry(change_frame)
        new_date_box = Entry(change_frame)
        new_mark_box = Entry(change_frame)
        old_label.grid(row=0, column=0)
        new_label.grid(row=0, column=2)
        Label(change_frame, text="Asignatura").grid(row=1, column=1)
        Label(change_frame, text="Fecha").grid(row=2, column=1)
        Label(change_frame, text="Nota").grid(row=3, column=1)
        old_subj_box.grid(row=1, column=0)
        old_date_box.grid(row=2, column=0)
        old_mark_box.grid(row=3, column=0)
        new_subj_box.grid(row=1, column=2)
        new_date_box.grid(row=2, column=2)
        new_mark_box.grid(row=3, column=2)

        save_button = Button(change_frame, text="Guardar",
                             command=lambda: self.app_modify_exam(old_subj_box.get(), old_date_box.get(),
                                                                  new_subj_box.get(),
                                                                  new_date_box.get(), new_mark_box.get(),
                                                                  err_communication, exams))
        save_button.grid(row=4, column=0, columnspan=3, pady=10)

        quit_button = Button(body_frame, text="QUIT", command=lambda: self.change_to_user_functionality(main_frame))
        quit_button.pack(pady=20)

        exams_frame.grid(padx=5, ipady=97, row=1, column=1)
        sub_title.pack()
        exams.pack()

    def delete_exam_scene(self, root):
        main_frame = Frame(root, borderwidth=constantes.FRAME_BORDERWIDTH, relief="groove")
        main_frame.pack()
        tittle = Label(main_frame, text="Eliminar Exámenes", font=(constantes.TITTLE_FONT, TITTLE_SIZE))
        tittle.grid(row=0, column=0, columnspan=2)
        err_comunication = Label(main_frame, text="", font=(constantes.SUBTITLE_FONT, ERR_MSG_SIZE), pady=10)

        exams_frame = Frame(main_frame, borderwidth=3, relief="groove")
        sub_title = Label(exams_frame, text="Tus exámenes:\t\t", justify=LEFT, font=(SUBTITLE_SIZE, SUBTITLE_SIZE))
        exams = Label(exams_frame, text=self.curr_user.exams.__str__(), justify=LEFT)

        sub_frame = Frame(main_frame, borderwidth=constantes.FRAME_BORDERWIDTH, relief="groove", padx=5, pady=5)
        sub_frame.grid(row=1, column=0, ipady=23)
        subj_label = Label(sub_frame, text="Asignatura*")
        date_label = Label(sub_frame, text="Fecha*")
        subj_label.grid(row=0, column=0)
        date_label.grid(row=1, column=0)
        subj_box = Entry(sub_frame)
        date_box = Entry(sub_frame)
        subj_box.grid(row=0, column=1)
        date_box.grid(row=1, column=1)
        buttons_frame = Frame(sub_frame)
        buttons_frame.grid(row=3, column=0, columnspan=2)
        confirm_button = Button(buttons_frame, text="DELETE",
                                command=lambda: self.app_delete_exam(subj_box.get(), date_box.get(),
                                                                     err_comunication, exams))
        quit_button = Button(buttons_frame, text="QUIT", command=lambda: self.change_to_user_functionality(main_frame))
        confirm_button.pack(side="left", pady=5)
        quit_button.pack(side="right", pady=5)

        err_comunication.grid(row=2, column=0, columnspan=2)
        exams_frame.grid(row=1, column=1)
        sub_title.pack()
        exams.pack()

    # == FUNCIONES AUXILIARES PARA BOTONES ==
    def apply_selection(self, subject, date, channel, old_subject_box, old_date_box, old_mark_box):
        valid, err_msg = self.validate_data(subject, date)

        if not valid:
            channel.config(text=err_msg, fg='red')
            return
        if date not in self.curr_user.exams.data[subject]:
            channel.config(text="Fecha no valida ", fg='red')
            return
        self.allow_mod = True
        channel.config(text="aplicando selección", fg="green")
        old_subject_box.config(state='normal')
        old_date_box.config(state='normal')
        old_mark_box.config(state='normal')
        old_subject_box.delete(0, END)
        old_date_box.delete(0, END)
        old_mark_box.delete(0, END)
        old_subject_box.insert(0, subject)
        old_date_box.insert(0, date)
        old_mark_box.insert(0, str(0))
        old_subject_box.config(state=DISABLED)
        old_date_box.config(state=DISABLED)
        old_mark_box.config(state=DISABLED)

import time
import re
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import os

import user
import constantes
import verificacion

PATH = os.path.dirname(__file__)[:-8]

TITTLE_SIZE = constantes.TITTLE_SIZE
SUBTITLE_SIZE = constantes.SUBTITLE_SIZE
ERR_MSG_SIZE = constantes.ERR_MSG_SIZE


class App:
    curr_user = None
    password_tries = constantes.PASSWORD_TRIES
    allow_mod = False

    def __init__(self):
        self.root = Tk()
        self.root.geometry(constantes.WINDOW_DIMENSSIONS)
        self.root.title(constantes.WINDOW_TITTLE)
        self.root.resizable(width=False, height=False)

        # Marco principal, se pasa como argumento a todoas las escenas
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill='both')

        # etiqueta accesible por todoslos elementos: comunica mensajes de error
        self.error_stream = Label(self.main_frame, text="", fg="red", font=(constantes.ERR_FONT, ERR_MSG_SIZE))
        self.error_stream.pack(side=BOTTOM, pady=0)

        # Primera escena
        self.log_in_scene(self.main_frame)

        # bucle principal
        self.root.mainloop()

    # == VALIDATE DATA ==
    @staticmethod
    def validate_date(date):
        if not re.match(r"^(2[0-9]{3})(-)(1[0-2]|0[1-9])(-)(3[01]|[12][0-9]|0[1-9])$", date):
            err_msg = "Fecha no válida"
            return False, err_msg
        return True, ""

    @staticmethod
    def validate_mark(mark):
        try:
            if mark == "":
                return True, ""
            mark = int(mark)
            if mark < 0:
                return False, "La nota debe ser mayor o igual que 0"
        except ValueError:
            return False, "La nota debe ser un número entero"
        return True, ""

    @staticmethod
    def validate_university(university: str):
        if len(university) <= 0:
            return False, "Universidad no puede ser un campo vacío"
        return True, ""

    @staticmethod
    def validate_age(age: str):
        try:
            if age == "":
                return False, "Edad no puede ser un campo vacío"
            age = int(age)
            if age < 0:
                return False, "La edad no puede ser negativa"
        except ValueError:
            return False, "La edad debe ser un número"
        return True, ""

    def validate_subject(self, subject, ev_existence=False):
        if len(subject) <= 0:
            return False, "campo de asignatura vacío"
        if ev_existence:
            if subject not in self.curr_user.subjects:
                return False, "asignatura no existente"
        if len(subject) > 15:
            return False, "nombre de asignatura demasiado largo"
        return True, ""

    def validate_date_existence(self, date, subject, tipo):
        valid_s, err_msg = self.validate_subject(subject, True)
        if not valid_s:
            print("Fatal_error: mal llamado a la función " + err_msg)
            return valid_s, err_msg
        valid, err_msg = self.validate_date(date)
        if not valid:
            return valid, err_msg
        if tipo == 'EXAM':
            if date not in self.curr_user.exams.data[subject]:
                return False, "no existe ese examen"
        elif tipo == 'PROJECT':
            if date not in self.curr_user.projects.data[subject]:
                return False, "no existe ese proyecto"
        else:
            print("Fatal error: mal llamado a la función")
            return None
        return True, ""

    # == FUNCIONALIDAD ==
    def error_stream_restore(self):
        self.error_stream.config(text="")

    def app_login_user(self, user_name, password, label, frame):
        label.config(text="")
        self.curr_user = user.login_user(user_name, password)
        if not self.curr_user:
            self.password_tries -= 1
            label.config(text="Bad log in")
        else:
            self.password_tries = 3
            self.change_to_user_functionality(frame)
            return
        if self.password_tries == 1:
            print("warning_message: fallos por numero de intentos")
            self.error_stream.config(text="Si fallas una vez más\nla aplicación se bloqueará 5 segundos")
        if self.password_tries == 0:
            print("Aplicación bloqueada: demasiados intentos")
            frame.destroy()
            time.sleep(5)
            self.password_tries = 3
            self.log_in_scene(self.main_frame)
            return

    def app_register_user(self, user_name, password, university, age, frame, root, bad_label):
        bad_label.config(text="")
        valid, err_msg = self.validate_university(university)
        if not valid:
            bad_label.config(text=err_msg)
            return

        valid, err_msg = self.validate_age(age)
        if not valid:
            bad_label.config(text=err_msg)
            return

        if not user.register_user(user_name, password, university, age):
            bad_label.config(text="bad name", font=(constantes.ERR_FONT, ERR_MSG_SIZE))
            return
        frame.destroy()
        self.log_in_scene(root)

    def app_add_exam(self, subject: str, date, nota, channel, exams):
        valid_s, err_msg = self.validate_subject(subject, True)
        if not valid_s:
            channel.config(text=err_msg, fg="red")
            return
        valid_s, err_msg = self.validate_date(date)
        if not valid_s:
            channel.config(text=err_msg, fg="red")
            return
        valid_s, err_msg = self.validate_mark(nota)
        if not valid_s:
            channel.config(text=err_msg, fg='red')
            return
        if nota == "":
            nota = -1
        if self.curr_user.add_exam(subject, date, nota):
            channel.config(text="Examen añadido", fg='green')
        else:
            channel.config(text="Examen ya registrado", fg="red")
        exams.config(text=self.curr_user.exams)

    def app_modify_exam(self, old_subject, old_date, new_subject, new_date, mark, channel, exams):
        channel.config(text="")
        if self.allow_mod:
            valid_s, err_msg = self.validate_subject(new_subject, True)
            if not valid_s:
                channel.config(text=err_msg, fg="red")
                return
            valid_s, err_msg = self.validate_date(new_date)
            if not valid_s:
                channel.config(text=err_msg, fg="red")
                return
            valid_s, err_msg = self.validate_mark(mark)
            if not valid_s:
                channel.config(text=err_msg, fg='red')
                return
            if mark == "":
                mark = -1
            if not self.curr_user.modify_exam(old_subject, old_date, new_subject, new_date, mark):
                print("FATAL ERROR: FALLO EN LA MODIFICACIÓN EN LA BASE DE DATOS")
                return
            exams.config(text=self.curr_user.exams.__str__())
            channel.config(text='Examen modificado', fg='green')
        else:
            channel.config(text="Selecciona primero un examen", fg='red')

    def app_delete_exam(self, subject, date, channel, exams):
        channel.config(text="")
        valid, err_msg = self.validate_date_existence(date, subject, 'EXAM')
        if not valid:
            channel.config(text=err_msg, fg='red')
            return
        if date in self.curr_user.exams.data[subject]:
            if not self.curr_user.drop_exam(subject, date):
                # si saltan estos print quiere decir que hubo un error en comprobaciones anteriores
                print("Fatal error: fecha que no existe")
                return
            channel.config(text="Examen eliminado", fg='green')
            exams.config(text=self.curr_user.exams)

    def app_add_subject(self, subject, channel, subjects):
        channel.config(text="")
        valid, err_msg = self.validate_subject(subject)
        if not valid:
            channel.config(text=err_msg, fg='red')
            return
        if subject in self.curr_user.subjects:
            channel.config(text="Esa asignatura ya existe", fg='red')
            return
        if not self.curr_user.add_subject(subject):
            print("Fatal error: la asignatura ya existe")
        else:
            channel.config(text="Asignatura añadida con éxito", fg='green')
        subjects.config(text=self.curr_user.str_subjects())

    def app_delete_subject(self, subject, channel, subjects_frame):
        valid, err_msg = self.validate_subject(subject, True)
        if not valid:
            channel.config(text=err_msg, fg='red')
            return
        if not self.curr_user.drop_subject(subject):
            print("FATAL ERROR: fallo al borrar la asignatura")
        else:
            channel.config(text="Asignatura eliminada con éxito", fg='green')
        subjects_frame.config(text=self.curr_user.str_subjects())

    def app_add_project(self, subject, date, mark, channel, projects):
        valid_s, err_msg = self.validate_subject(subject, True)
        if not valid_s:
            channel.config(text=err_msg, fg="red")
            return
        valid_s, err_msg = self.validate_date(date)
        if not valid_s:
            channel.config(text=err_msg, fg="red")
            return
        valid_s, err_msg = self.validate_mark(mark)
        if not valid_s:
            channel.config(text=err_msg, fg='red')
            return
        if mark == "":
            mark = -1
        if self.curr_user.add_project(subject, date, mark):
            channel.config(text="Proyecto añadido", fg='green')
        else:
            channel.config(text="Proyecto ya registrado", fg="red")
        projects.config(text=self.curr_user.projects)

    def app_modify_project(self, old_subject, old_date, new_subject, new_date, mark, channel, projects):
        channel.config(text="")
        if self.allow_mod:
            valid_s, err_msg = self.validate_subject(new_subject, True)
            if not valid_s:
                channel.config(text=err_msg, fg="red")
                return
            valid_s, err_msg = self.validate_date(new_date)
            if not valid_s:
                channel.config(text=err_msg, fg="red")
                return
            valid_s, err_msg = self.validate_mark(mark)
            if not valid_s:
                channel.config(text=err_msg, fg='red')
                return
            if mark == "":
                mark = -1
            if not self.curr_user.modify_project(old_subject, old_date, new_subject, new_date, mark):
                print("FATAL ERROR: FALLO EN LA MODIFICACIÓN EN LA BASE DE DATOS")
                return
            projects.config(text=self.curr_user.projects.__str__())
            channel.config(text='Proyecto modificado', fg='green')
        else:
            channel.config(text="Selecciona primero un proyecto", fg='red')

    def app_delete_project(self, subject, date, channel, projects):
        channel.config(text="")
        valid, err_msg = self.validate_date_existence(date, subject, 'PROJECT')
        if not valid:
            channel.config(text=err_msg, fg='red')
            return
        if date in self.curr_user.projects.data[subject]:
            if not self.curr_user.drop_project(subject, date):
                # si saltan estos print quiere decir que hubo un error en comprobaciones anteriores
                print("Fatal error: fecha que no existe")
                return
            channel.config(text="Projecto eliminado", fg='green')
            projects.config(text=self.curr_user.projects.__str__())

    def app_verify_all(self, m_file, s_file, chain_cert, sys_cert):
        if len(m_file)*len(s_file)*len(chain_cert)*len(sys_cert) == 0:
            self.error_stream.config(text="Campo vacío", fg="red")
            return -1
        err_code = verificacion.verify_all(m_file, s_file, chain_cert, sys_cert)
        self.error_stream_restore()
        match err_code:
            case -1:
                self.error_stream.config(text="Certificado AC1 defectuoso o modificado", fg="red")
            case -2:
                self.error_stream.config(text="Certificado de sistema defectuoso o modificado", fg="red")
            case -3:
                self.error_stream.config(text="Certificado de sistema no válido", fg="red")
            case -4:
                self.error_stream.config(text="Certificado de AC1 no válido", fg="red")
            case -5:
                self.error_stream.config(text="Firma no válida", fg="red")
            case _:
                self.error_stream.config(text="Certificado y firma validada", fg="green")

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
        self.allow_mod = False
        self.error_stream_restore()
        frame.destroy()
        self.modify_exam_scene(self.main_frame)

    def change_to_delete_exam_scene(self, frame):
        self.error_stream_restore()
        frame.destroy()
        self.delete_exam_scene(self.main_frame)

    def change_to_subject_scene(self, frame):
        self.error_stream_restore()
        frame.destroy()
        self.subject_scene(self.main_frame)

    def change_to_add_subj_scene(self, frame):
        self.error_stream_restore()
        frame.destroy()
        self.add_subject_scene(self.main_frame)

    def change_to_delete_subj_scene(self, frame):
        self.error_stream_restore()
        frame.destroy()
        self.delete_subject_scene(self.main_frame)

    def change_to_project_scene(self, frame):
        self.error_stream_restore()
        frame.destroy()
        self.project_scene(self.main_frame)

    def change_to_add_project(self, frame):
        self.error_stream_restore()
        frame.destroy()
        self.add_project_scene(self.main_frame)

    def change_to_modify_project_scene(self, frame):
        self.allow_mod = False
        self.error_stream_restore()
        frame.destroy()
        self.modify_project_scene(self.main_frame)

    def change_to_delete_project_scene(self, frame):
        self.error_stream_restore()
        frame.destroy()
        self.delete_project_scene(self.main_frame)

    def change_to_mark_scene(self, frame):
        self.error_stream_restore()
        frame.destroy()
        self.marks_scene(self.main_frame)

    def change_to_my_data(self, frame):
        self.error_stream_restore()
        frame.destroy()
        self.my_data_scene(self.main_frame)

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
        university_label = Label(main_frame, text="Universidad::")
        university_box = Entry(main_frame)
        age_label = Label(main_frame, text="Edad:")
        age_box = Entry(main_frame)
        university_label.pack()
        university_box.pack()
        age_label.pack()
        age_box.pack()
        sub_frame = Frame(main_frame)
        sub_frame.pack()
        bad_name = Label(main_frame, text="", fg='red')
        bad_name.pack(side=BOTTOM)
        register_button = Button(sub_frame, text="registrar",
                                 command=lambda: self.app_register_user(user_name_box.get(), user_pw_box.get(),
                                                                        university_box.get(), age_box.get(),
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
        sub_title.grid(row=0, column=0, columnspan=6, ipady=10)
        subj_button = Button(sub_frame, text="Asignaturas", command=lambda: self.change_to_subject_scene(main_frame))
        subj_button.grid(row=1, column=0)
        exams_button = Button(sub_frame, text="Exams", command=lambda: self.change_to_exam_scene(main_frame))
        exams_button.grid(row=1, column=1)
        project_button = Button(sub_frame, text="Projects",
                                command=lambda: self.change_to_project_scene(main_frame))
        project_button.grid(row=1, column=2)
        marks_button = Button(sub_frame, text="Mis notas", command=lambda: self.change_to_mark_scene(main_frame))
        marks_button.grid(row=1, column=3)
        my_data_button = Button(sub_frame, text="Mis datos", command=lambda: self.change_to_my_data(main_frame))
        my_data_button.grid(row=1, column=5)
        exit_button = Button(sub_frame, text="Salir", command=lambda: self.change_to_log_in(main_frame))
        exit_button.grid(row=2, column=0, pady=50, columnspan=6)

    def exam_scene(self, root):
        main_frame = ttk.Frame(root)
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
        main_frame = Frame(root)
        main_frame.pack()
        tittle = Label(main_frame, text="Añadir Exámenes", font=(constantes.TITTLE_FONT, TITTLE_SIZE))
        tittle.grid(row=0, column=0, columnspan=2)
        err_comunication = Label(main_frame, text="", font=(constantes.SUBTITLE_FONT, ERR_MSG_SIZE), pady=10)

        exams_frame = Frame(main_frame, borderwidth=3, relief="groove")
        sub_title = Label(exams_frame, text="Tus exámenes:\t\t", justify=LEFT, font=(SUBTITLE_SIZE, SUBTITLE_SIZE))
        exams = Label(exams_frame, text=self.curr_user.exams.__str__(), justify=LEFT)

        sub_frame = Frame(main_frame, borderwidth=constantes.FRAME_BORDERWIDTH, relief="groove", padx=5, pady=5)
        sub_frame.grid(row=1, column=0, ipady=23)
        subj_label = Label(sub_frame, text="Asignatura*")
        date_label = Label(sub_frame, text="Fecha*\n[YYYY-MM-DD]")
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
        tittle = Label(main_frame, text="Modificar Exámenes", font=(constantes.TITTLE_FONT, TITTLE_SIZE))
        tittle.grid(row=0, column=0, columnspan=2, ipady=10)
        body_frame = Frame(main_frame, borderwidth=constantes.FRAME_BORDERWIDTH, relief="groove")
        body_frame.grid(row=1, column=0)

        exams_frame = Frame(main_frame, borderwidth=constantes.FRAME_BORDERWIDTH, relief="groove")
        sub_title = Label(exams_frame, text="Tus exámenes:\t\t", justify=LEFT, font=(SUBTITLE_SIZE, SUBTITLE_SIZE))
        exams = Label(exams_frame, text=self.curr_user.exams.__str__(), justify=LEFT)

        select_frame = Frame(body_frame, borderwidth=constantes.FRAME_BORDERWIDTH, relief="groove")
        select_frame.pack(ipady=5)
        err_communication = Label(select_frame, text="", font=(constantes.ERR_FONT, ERR_MSG_SIZE), pady=5)
        select_subj = Entry(select_frame)
        select_date = Entry(select_frame)
        select_subj_label = Label(select_frame, text="Asignatura")
        select_date_label = Label(select_frame, text="Fecha\n[YYYY-MM-DD]")
        select_label = Label(select_frame, text="Seleccion:")
        apply_button = Button(select_frame, text="Aplicar selección",
                              command=lambda: self.apply_selection_exam(select_subj.get(), select_date.get(),
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
        Label(change_frame, text="Fecha\n[YYYY-MM-DD]").grid(row=2, column=1)
        Label(change_frame, text="Nota").grid(row=3, column=1)
        old_subj_box.grid(row=1, column=0)
        old_date_box.grid(row=2, column=0)
        old_mark_box.grid(row=3, column=0)
        new_subj_box.grid(row=1, column=2)
        new_date_box.grid(row=2, column=2)
        new_mark_box.grid(row=3, column=2)

        save_button = Button(change_frame, text="Guardar",
                             command=lambda: self.app_modify_exam(old_subj_box.get(), old_date_box.get(),
                                                                  new_subj_box.get(), new_date_box.get(),
                                                                  new_mark_box.get(), err_communication, exams))
        save_button.grid(row=4, column=0, columnspan=3, pady=10)

        quit_button = Button(body_frame, text="QUIT", command=lambda: self.change_to_user_functionality(main_frame))
        quit_button.pack(pady=20)

        exams_frame.grid(padx=5, ipady=97, row=1, column=1)
        sub_title.pack()
        exams.pack()

    def delete_exam_scene(self, root):
        main_frame = Frame(root)
        main_frame.pack()
        tittle = Label(main_frame, text="Eliminar Exámenes", font=(constantes.TITTLE_FONT, TITTLE_SIZE))
        tittle.grid(row=0, column=0, columnspan=2)
        err_comunication = Label(main_frame, text="", font=(constantes.SUBTITLE_FONT, ERR_MSG_SIZE), pady=10)

        exams_frame = Frame(main_frame, borderwidth=constantes.FRAME_BORDERWIDTH, relief="groove")
        sub_title = Label(exams_frame, text="Tus exámenes:\t\t", justify=LEFT, font=(SUBTITLE_SIZE, SUBTITLE_SIZE))
        exams = Label(exams_frame, text=self.curr_user.exams.__str__(), justify=LEFT)

        sub_frame = Frame(main_frame, borderwidth=constantes.FRAME_BORDERWIDTH, relief="groove", padx=5, pady=5)
        sub_frame.grid(row=1, column=0, ipady=23)
        subj_label = Label(sub_frame, text="Asignatura*")
        date_label = Label(sub_frame, text="Fecha*\n[YYYY-MM-DD]")
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

    def subject_scene(self, root):
        main_frame = ttk.Frame(root)
        main_frame.pack()
        tittle = Label(main_frame, text="Gestión de asignaturas", font=(constantes.TITTLE_FONT, TITTLE_SIZE))
        tittle.pack(pady=10, fill="x")
        sub_frame = ttk.Frame(main_frame, borderwidth=constantes.FRAME_BORDERWIDTH, relief="groove")
        sub_frame.pack()
        sub_title = Label(sub_frame, text="Tus Asignaturas:\t", justify=LEFT,
                          font=(constantes.SUBTITLE_FONT, SUBTITLE_SIZE))
        sub_title.pack()
        subjects = Label(sub_frame, text=self.curr_user.str_subjects(), justify=LEFT)
        subjects.pack()
        actions_frame = ttk.Frame(main_frame)
        actions_frame.pack()
        add_button = Button(actions_frame, text="ADD", command=lambda: self.change_to_add_subj_scene(main_frame))
        add_button.grid(row=0, column=0)
        del_button = Button(actions_frame, text="DELETE", command=lambda: self.change_to_delete_subj_scene(main_frame))
        del_button.grid(row=0, column=1)
        quit_button = Button(main_frame, text="BACK", command=lambda: self.change_to_user_functionality(main_frame))
        quit_button.pack()

    def add_subject_scene(self, root):
        main_frame = Frame(root)
        main_frame.pack()
        tittle = Label(main_frame, text="Añadir Asignatura", font=(constantes.TITTLE_FONT, TITTLE_SIZE))
        tittle.grid(row=0, column=0, columnspan=2)
        err_comunication = Label(main_frame, text="", font=(constantes.SUBTITLE_FONT, ERR_MSG_SIZE), pady=10)

        body_frame = Frame(main_frame)
        body_frame.grid(row=1, column=0, pady=20)

        subjects_frame = Frame(body_frame, borderwidth=3, relief="groove")
        sub_title = Label(subjects_frame, text="Tus asignaturas:\t", justify=LEFT, font=(SUBTITLE_SIZE, SUBTITLE_SIZE))
        subjects = Label(subjects_frame, text=self.curr_user.str_subjects(), justify=LEFT)

        sub_frame = Frame(body_frame, borderwidth=constantes.FRAME_BORDERWIDTH, relief="groove", padx=5, pady=5)
        sub_frame.grid(row=1, column=0, ipady=23, pady=20)
        subj_label = Label(sub_frame, text="Asignatura*")
        subj_label.grid(row=0, column=0)
        subj_box = Entry(sub_frame)
        subj_box.grid(row=0, column=1)

        buttons_frame = Frame(sub_frame)
        buttons_frame.grid(row=3, column=0, columnspan=2)
        confirm_button = Button(buttons_frame, text="ADD",
                                command=lambda: self.app_add_subject(subj_box.get(),
                                                                     err_comunication, subjects))
        quit_button = Button(buttons_frame, text="QUIT", command=lambda: self.change_to_user_functionality(main_frame))
        confirm_button.pack(side="left", pady=5)
        quit_button.pack(side="right", pady=5)

        err_comunication.grid(row=2, column=0, columnspan=2)
        subjects_frame.grid(row=1, column=1)
        sub_title.pack()
        subjects.pack()

    def delete_subject_scene(self, root):
        main_frame = Frame(root)
        main_frame.pack()
        tittle = Label(main_frame, text="Eliminar Asignatura", font=(constantes.TITTLE_FONT, TITTLE_SIZE))
        tittle.grid(row=0, column=0, columnspan=2)
        err_comunication = Label(main_frame, text="", font=(constantes.SUBTITLE_FONT, ERR_MSG_SIZE), pady=10)

        body_frame = Frame(main_frame)
        body_frame.grid(row=1, column=0, pady=20)

        subjects_frame = Frame(body_frame, borderwidth=3, relief="groove")
        sub_title = Label(subjects_frame, text="Tus asignaturas:\t", justify=LEFT, font=(SUBTITLE_SIZE, SUBTITLE_SIZE))
        subjects = Label(subjects_frame, text=self.curr_user.str_subjects(), justify=LEFT)

        sub_frame = Frame(body_frame, borderwidth=constantes.FRAME_BORDERWIDTH, relief="groove", padx=5, pady=5)
        sub_frame.grid(row=1, column=0, ipady=23, pady=20)
        subj_label = Label(sub_frame, text="Asignatura*")
        subj_label.grid(row=0, column=0)
        subj_box = Entry(sub_frame)
        subj_box.grid(row=0, column=1)

        buttons_frame = Frame(sub_frame)
        buttons_frame.grid(row=3, column=0, columnspan=2)
        confirm_button = Button(buttons_frame, text="DELETE",
                                command=lambda: self.app_delete_subject(subj_box.get(),
                                                                        err_comunication, subjects))
        quit_button = Button(buttons_frame, text="QUIT", command=lambda: self.change_to_user_functionality(main_frame))
        confirm_button.pack(side="left", pady=5)
        quit_button.pack(side="right", pady=5)

        err_comunication.grid(row=2, column=0, columnspan=2)
        subjects_frame.grid(row=1, column=1)
        sub_title.pack()
        subjects.pack()
        warning_label = Label(main_frame,
                              text="Si eliminas una asignatura, se borrarán todos los examenes"
                                   " y proyectos asociados a ella",
                              font=(constantes.ERR_FONT, constantes.WARNING_SIZE), fg='black')
        warning_label.grid(row=3, column=0, columnspan=2)

    def project_scene(self, root):
        main_frame = ttk.Frame(root)
        main_frame.pack()
        tittle = Label(main_frame, text="Gestión de projectos", font=(constantes.TITTLE_FONT, TITTLE_SIZE))
        tittle.pack(pady=10, fill="x")
        sub_frame = ttk.Frame(main_frame, borderwidth=constantes.FRAME_BORDERWIDTH, relief="groove")
        sub_frame.pack()
        sub_title = Label(sub_frame, text="Tus proyectos:\t\t", justify=LEFT,
                          font=(constantes.SUBTITLE_FONT, SUBTITLE_SIZE))
        sub_title.pack()
        project_dict = self.curr_user.projects
        projects = Label(sub_frame, text=project_dict.__str__(), justify=LEFT)
        projects.pack()
        actions_frame = ttk.Frame(main_frame)
        actions_frame.pack()
        add_button = Button(actions_frame, text="ADD", command=lambda: self.change_to_add_project(main_frame))
        add_button.grid(row=0, column=0)
        mod_button = Button(actions_frame, text="MODIFY",
                            command=lambda: self.change_to_modify_project_scene(main_frame))
        mod_button.grid(row=0, column=1)
        del_button = Button(actions_frame, text="DELETE",
                            command=lambda: self.change_to_delete_project_scene(main_frame))
        del_button.grid(row=0, column=2)
        quit_button = Button(main_frame, text="Back", command=lambda: self.change_to_user_functionality(main_frame))
        quit_button.pack()

    def add_project_scene(self, root):
        main_frame = Frame(root)
        main_frame.pack()
        tittle = Label(main_frame, text="Añadir Poryectos", font=(constantes.TITTLE_FONT, TITTLE_SIZE))
        tittle.grid(row=0, column=0, columnspan=2)
        err_communication = Label(main_frame, text="", font=(constantes.SUBTITLE_FONT, ERR_MSG_SIZE), pady=10)

        projects_frame = Frame(main_frame, borderwidth=3, relief="groove")
        sub_title = Label(projects_frame, text="Tus proyectos:\t\t", justify=LEFT, font=(SUBTITLE_SIZE, SUBTITLE_SIZE))
        projects = Label(projects_frame, text=self.curr_user.projects.__str__(), justify=LEFT)

        sub_frame = Frame(main_frame, borderwidth=constantes.FRAME_BORDERWIDTH, relief="groove", padx=5, pady=5)
        sub_frame.grid(row=1, column=0, ipady=23)
        subj_label = Label(sub_frame, text="Asignatura*")
        date_label = Label(sub_frame, text="Fecha*\n[YYYY-MM-DD]")
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
                                command=lambda: self.app_add_project(subj_box.get(), date_box.get(), mark_box.get(),
                                                                     err_communication, projects))
        quit_button = Button(buttons_frame, text="QUIT", command=lambda: self.change_to_user_functionality(main_frame))
        confirm_button.pack(side="left", pady=5)
        quit_button.pack(side="right", pady=5)

        err_communication.grid(row=2, column=0, columnspan=2)
        projects_frame.grid(row=1, column=1)
        sub_title.pack()
        projects.pack()

    def modify_project_scene(self, root):
        main_frame = Frame(root)
        main_frame.pack()
        tittle = Label(main_frame, text="Modificar Proyectos", font=(constantes.TITTLE_FONT, TITTLE_SIZE))
        tittle.grid(row=0, column=0, columnspan=2, ipady=10)
        body_frame = Frame(main_frame, borderwidth=constantes.FRAME_BORDERWIDTH, relief="groove")
        body_frame.grid(row=1, column=0)

        projects_frame = Frame(main_frame, borderwidth=constantes.FRAME_BORDERWIDTH, relief="groove")
        sub_title = Label(projects_frame, text="Tus proyectos:\t\t", justify=LEFT, font=(SUBTITLE_SIZE, SUBTITLE_SIZE))
        projects = Label(projects_frame, text=self.curr_user.projects.__str__(), justify=LEFT)

        select_frame = Frame(body_frame, borderwidth=constantes.FRAME_BORDERWIDTH, relief="groove")
        select_frame.pack(ipady=5, ipadx=5)
        err_communication = Label(select_frame, text="", font=(constantes.ERR_FONT, ERR_MSG_SIZE), pady=5)
        select_subj = Entry(select_frame)
        select_date = Entry(select_frame)
        select_subj_label = Label(select_frame, text="Asignatura")
        select_date_label = Label(select_frame, text="Fecha\n[YYYY-MM-DD]")
        select_label = Label(select_frame, text="Seleccion:")
        apply_button = Button(select_frame, text="Aplicar selección",
                              command=lambda: self.apply_selection_project(select_subj.get(), select_date.get(),
                                                                           err_communication, old_subj_box,
                                                                           old_date_box,
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
        Label(change_frame, text="Fecha\n[YYYY-MM-DD]").grid(row=2, column=1)
        Label(change_frame, text="Nota").grid(row=3, column=1)
        old_subj_box.grid(row=1, column=0)
        old_date_box.grid(row=2, column=0)
        old_mark_box.grid(row=3, column=0)
        new_subj_box.grid(row=1, column=2)
        new_date_box.grid(row=2, column=2)
        new_mark_box.grid(row=3, column=2)

        save_button = Button(change_frame, text="Guardar",
                             command=lambda: self.app_modify_project(old_subj_box.get(), old_date_box.get(),
                                                                     new_subj_box.get(),
                                                                     new_date_box.get(), new_mark_box.get(),
                                                                     err_communication, projects))
        save_button.grid(row=4, column=0, columnspan=3, pady=10)

        quit_button = Button(body_frame, text="QUIT", command=lambda: self.change_to_user_functionality(main_frame))
        quit_button.pack(pady=20)

        projects_frame.grid(padx=5, ipady=97, row=1, column=1)
        sub_title.pack()
        projects.pack()

    def delete_project_scene(self, root):
        main_frame = Frame(root)
        main_frame.pack()
        tittle = Label(main_frame, text="Eliminar Proyectos", font=(constantes.TITTLE_FONT, TITTLE_SIZE))
        tittle.grid(row=0, column=0, columnspan=2)
        err_communication = Label(main_frame, text="", font=(constantes.SUBTITLE_FONT, ERR_MSG_SIZE), pady=10)

        projects_frame = Frame(main_frame, borderwidth=constantes.FRAME_BORDERWIDTH, relief="groove")
        sub_title = Label(projects_frame, text="Tus proyectos:\t\t", justify=LEFT, font=(SUBTITLE_SIZE, SUBTITLE_SIZE))
        projects = Label(projects_frame, text=self.curr_user.projects.__str__(), justify=LEFT)

        sub_frame = Frame(main_frame, borderwidth=constantes.FRAME_BORDERWIDTH, relief="groove", padx=5, pady=5)
        sub_frame.grid(row=1, column=0, ipady=23)
        subj_label = Label(sub_frame, text="Asignatura*")
        date_label = Label(sub_frame, text="Fecha*\n[YYYY-MM-DD]")
        subj_label.grid(row=0, column=0)
        date_label.grid(row=1, column=0)
        subj_box = Entry(sub_frame)
        date_box = Entry(sub_frame)
        subj_box.grid(row=0, column=1)
        date_box.grid(row=1, column=1)
        buttons_frame = Frame(sub_frame)
        buttons_frame.grid(row=3, column=0, columnspan=2)
        confirm_button = Button(buttons_frame, text="DELETE",
                                command=lambda: self.app_delete_project(subj_box.get(), date_box.get(),
                                                                        err_communication, projects))
        quit_button = Button(buttons_frame, text="QUIT", command=lambda: self.change_to_user_functionality(main_frame))
        confirm_button.pack(side="left", pady=5)
        quit_button.pack(side="right", pady=5)

        err_communication.grid(row=2, column=0, columnspan=2)
        projects_frame.grid(row=1, column=1)
        sub_title.pack()
        projects.pack()

    def marks_scene(self, root):
        main_frame = Frame(root)
        main_frame.pack()

        tittle = Label(main_frame, text="Tus notas", font=(constantes.TITTLE_FONT, TITTLE_SIZE))

        body = Frame(main_frame, borderwidth=constantes.FRAME_BORDERWIDTH, relief="groove")

        exams_frame = Frame(body)
        scroll_exams = Scrollbar(exams_frame, orient=VERTICAL)
        notas_exam = Listbox(exams_frame, yscrollcommand=scroll_exams.set)
        scroll_exams.config(command=notas_exam.yview)

        projects_frame = Frame(body)
        scroll_project = Scrollbar(projects_frame, orient=VERTICAL)
        notas_project = Listbox(projects_frame, yscrollcommand=scroll_project.set)
        scroll_project.config(command=notas_project.yview)

        exam_label = Label(body, text="Exámenes:")
        project_label = Label(body, text="Proyectos:")
        quit_button = Button(body, text="Quit", command=lambda: self.change_to_user_functionality(main_frame))

        select_fm = Frame(body)
        subj_box = Entry(select_fm)
        select_lb = Label(select_fm, text="Asignatura:")
        err_channel = Label(select_fm, text="", font=(constantes.ERR_FONT, constantes.ERR_MSG_SIZE))
        select_button = Button(select_fm, text="APPLY",
                               command=lambda: self.apply_selection_mark(subj_box.get(), notas_exam, notas_project,
                                                                         err_channel))

        tittle.pack()
        body.pack(pady=20)

        select_fm.grid(row=0, column=0, columnspan=2)
        exam_label.grid(row=1, column=0)
        project_label.grid(row=1, column=1)
        exams_frame.grid(row=2, column=0, pady=10, padx=10)
        projects_frame.grid(row=2, column=1, pady=10, padx=10)
        quit_button.grid(row=3, column=0, columnspan=2, pady=20)

        select_lb.grid(row=0, column=0, pady=5)
        subj_box.grid(row=0, column=1, pady=5)
        select_button.grid(row=1, column=0, columnspan=2)
        err_channel.grid(row=2, column=0, columnspan=2)

        notas_exam.pack(side=LEFT)
        scroll_exams.pack(sid=RIGHT, fill=BOTH)
        notas_project.pack(side=LEFT)
        scroll_project.pack(side=RIGHT, fill=BOTH)

    def my_data_scene(self, root):
        main_frame = Frame(root)
        tittle = Label(main_frame, text="Tus datos", font=(constantes.TITTLE_FONT, constantes.TITTLE_SIZE))

        body = Frame(main_frame, borderwidth=constantes.FRAME_BORDERWIDTH, relief='groove')
        user_name, university, age = self.curr_user.get_user_data()
        data_str = "Nombre: " + user_name + "\n\t" + "Universidad: " + university + "\n" + "Edad: " + age
        data_label = Label(body, text=data_str, font=(constantes.SUBTITLE_FONT, constantes.SUBTITLE_SIZE))
        main_frame.pack()
        tittle.pack()
        body.pack()
        data_label.pack(ipadx=10)
        exit_button = Button(main_frame, text="Salir", command=lambda: self.change_to_user_functionality(main_frame))
        download = Button(main_frame, text="Descargar certificado de notas", command=lambda: self.marks_certification())
        download.pack()
        validate_fm = Frame(main_frame, borderwidth=constantes.FRAME_BORDERWIDTH, relief='groove')
        validate_fm.pack()
        exit_button.pack()
        validate_title = Label(validate_fm, text="Valida tus notas", font=(constantes.TITTLE_FONT, SUBTITLE_SIZE))
        message = Label(validate_fm, text="Mensaje")
        sign = Label(validate_fm, text="Firma")
        ac1 = Label(validate_fm, text="AC1cert")
        a = Label(validate_fm, text="Acert")
        s_file = Entry(validate_fm, state=DISABLED, width=40)
        m_file = Entry(validate_fm, state=DISABLED, width=40)
        a1cert = Entry(validate_fm, state=DISABLED, width=40)
        acert = Entry(validate_fm, state=DISABLED, width=40)
        m_explore = Button(validate_fm, text="Select marks file",
                           command=lambda: self.m_browser(m_file, ("Marks file", ".txt")))
        s_explore = Button(validate_fm, text="Select sign file",
                           command=lambda: self.m_browser(s_file, ("Sign file", ".sig")))
        ac1_explore = Button(validate_fm, text="Select certchain file",
                             command=lambda: self.m_browser(a1cert, ("Concat certificate", ".pem")))
        a_explore = Button(validate_fm, text="Select cert file",
                           command=lambda: self.m_browser(acert, ("system certificate", ".pem")))

        validate_button = Button(validate_fm, text="Validate",
                                 command=lambda: self.app_verify_all(m_file.get(), s_file.get(), a1cert.get(),
                                                                     acert.get()))
        validate_title.grid(row=0, column=0, columnspan=2)
        message.grid(row=1, column=0, pady=5)
        sign.grid(row=3, column=0, pady=5)
        m_file.grid(row=1, column=1, pady=5, padx=5)
        s_file.grid(row=3, column=1, pady=5, padx=5)
        m_explore.grid(row=2, column=0, columnspan=2, pady=5)
        s_explore.grid(row=4, column=0, columnspan=2, pady=5)
        ac1.grid(row=5, column=0, pady=5)
        a1cert.grid(row=5, column=1, pady=5)
        ac1_explore.grid(row=6, column=0, columnspan=2, pady=5)
        a.grid(row=7, column=0, pady=5)
        acert.grid(row=7, column=1, pady=5)
        a_explore.grid(row=8, column=0, columnspan=2, pady=5)

        validate_button.grid(row=9, column=0, columnspan=2, pady=5)

    def m_browser(self, box, looking_for):
        m_filename = filedialog.askopenfilename(initialdir=PATH + "src/" + self.curr_user.user_name + "_datos/",
                                                title="select file", filetypes=(looking_for, ))
        box.config(state='normal')
        box.delete(0, END)
        box.insert(0, m_filename)
        box.config(state=DISABLED)
        print("selected file: ", m_filename)

    # == FUNCIONES AUXILIARES PARA BOTONES ==

    def marks_certification(self):
        self.curr_user.gen_data()
        return

    def apply_selection_exam(self, subject, date, channel, old_subject_box, old_date_box, old_mark_box):
        valid_s, err_msg = self.validate_date_existence(date, subject, 'EXAM')
        if not valid_s:
            channel.config(text=err_msg, fg='red')
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
        mark = self.curr_user.check_event_mark(subject, date, 'EXAM')
        if mark == -1:
            mark = "sin nota..."
        old_mark_box.insert(0, str(mark))
        old_subject_box.config(state=DISABLED)
        old_date_box.config(state=DISABLED)
        old_mark_box.config(state=DISABLED)

    def apply_selection_project(self, subject, date, channel, old_subject_box, old_date_box, old_mark_box):
        valid_s, err_msg = self.validate_date_existence(date, subject, 'PROJECT')
        if not valid_s:
            channel.config(text=err_msg, fg='red')
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
        mark = self.curr_user.check_event_mark(subject, date, 'PROJECT')
        if mark == -1:
            mark = "sin nota..."
        old_mark_box.insert(0, str(mark))
        old_subject_box.config(state=DISABLED)
        old_date_box.config(state=DISABLED)
        old_mark_box.config(state=DISABLED)

    def apply_selection_mark(self, subject, list_box_exams, list_box_projects, err_channel):
        valid, err_msg = self.validate_subject(subject, True)
        if not valid:
            err_channel.config(text=err_msg, fg='red')
            return
        err_channel.config(text="Aplicando selección", fg='green')
        list_box_exams.delete(0, END)
        list_box_projects.delete(0, END)
        for e in self.curr_user.exams.data[subject]:
            mark = self.curr_user.check_event_mark(subject, e, 'EXAM')
            if mark == -1:
                mark = "sin nota..."
            list_box_exams.insert(END, e + " = " + str(mark))

        for e in self.curr_user.projects.data[subject]:
            mark = self.curr_user.check_event_mark(subject, e, 'PROJECT')
            if mark == -1:
                mark = "sin nota..."
            list_box_projects.insert(END, e + " = " + str(mark))

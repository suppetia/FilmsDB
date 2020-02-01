"""
@author Christopher Mertens
"""

import os
from tkinter import Label, Button, Entry, Menu, Listbox, Scrollbar, Toplevel, Checkbutton
from tkinter import messagebox, filedialog
from tkinter import N, E, S, W, END, RIGHT, BOTTOM, LEFT, BOTH, StringVar, IntVar, ACTIVE
from PIL import ImageTk, Image

from private_db.films.FilmeDB import *
from private_db.films.FilmImport import *


class DB_GUI:
    """ gui to display a FilmDB and query it """

    # standard directory for filedialogs
    STANDARD_DB_DIR = "..\\my_db"
    # standard directory for cover pictures
    STANDARD_COVER_IMG_DIR = os.path.join(STANDARD_DB_DIR, "cover_images")
    # standard cover picture if no cover is stored
    STANDARD_IMG_COVER = os.path.join(STANDARD_COVER_IMG_DIR, "image_not_found.gif")
    # standard db is saved in "settings.conf"
    SETTINGS_FILE_NAME = os.path.join("settings.conf")
    # standard online database to import film information from
    STANDARD_ONLINE_DB = 'imdb'
    # standard default disc type
    STANDARD_DISC_TYPE = 0

    def __init__(self, master):

        # root panel
        self.master = master
        master.geometry("600x570")

        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

        # load settings
        conf = DB_GUI.load_settings()
        self.cover_img_dir = conf['cover_img_dir']
        self.private_db_dir = conf['private_db_dir']
        self.default_cover = conf['default_cover']
        self.default_online_db = conf['online_db']
        self.translate_genres = bool(conf['translate_genres'])
        self.default_disc_type = int(conf['default_disc_type'])
        print(conf)

        # menu bar
        menu = Menu(master)

        menu_file = Menu(menu, tearoff=0)
        menu_file.add_command(label="Neue Datenbank", command=lambda: self.change_db(create_new=True))
        menu_file.add_command(label="Datenbank öffnen", command=lambda: self.change_db(create_new=False))
        menu_file.add_command(label="Speichern", command=self.save_db)
        menu_file.add_separator()
        menu_file.add_command(label="Datenbank exportieren", command=self.export_db)
        menu_file.add_command(label="Daten importieren", command=self.import_db)
        menu_file.add_separator()
        menu_file.add_command(label="Schließen", command=self.on_closing)
        menu.add_cascade(label="Datei", menu=menu_file)

        menu.add_separator()

        menu_films = Menu(menu, tearoff=0)
        menu_films.add_command(label="Film hinzufügen", command=lambda: WindowFilmEdit(self, self.db, "add"))
        menu_films.add_command(label="Film bearbeiten", command=lambda: WindowFilmEdit(self, self.db, "edit"))
        menu_films.add_command(label="Film löschen", command=lambda: WindowFilmEdit(self, self.db, "remove"))

        menu.add_cascade(label="Filme", menu=menu_films)

        master.config(menu=menu)

        # search interface

        self.query = StringVar()
        self.query.set("")

        lbl_query = Label(master, text="Suche", font=("Calibri", "11", "bold"))
        lbl_query.grid(row=0, column=0, sticky=W+S, padx=5)

        lbl_query_categories = Label(master, text="in Suchkategorien:")
        lbl_query_categories.grid(row=0, column=1, sticky=W)

        self.entry_query = Entry(master, text="Suche", textvariable=self.query)
        self.entry_query.grid(row=3, column=0, padx=5, pady=5, sticky=W+E+S, columnspan=4)
        self.entry_query.config(width=40)

        self.entry_query.bind("<KeyRelease>", self.film_query)

        self.btn_query = Button(master, text="Suchen", command=self.film_query, width=10)
        self.btn_query.grid(row=3, column=4, padx=5, sticky=W)

        # query checkbuttons

        self.search_for_title = IntVar()
        cbtn_title = Checkbutton(master, text="Titel", variable=self.search_for_title)
        cbtn_title.select()
        cbtn_title.grid(row=1, column=0, padx=5, pady=5, sticky=W)

        self.search_for_release_year = IntVar()
        cbtn_release_year = Checkbutton(master, text="Veröffentlichungsjahr", variable=self.search_for_release_year)
        cbtn_release_year.select()
        cbtn_release_year.grid(row=1, column=1, padx=5, pady=5, sticky=W)

        self.search_for_director = IntVar()
        cbtn_director = Checkbutton(master, text="Regisseur", variable=self.search_for_director)
        cbtn_director.select()
        cbtn_director.grid(row=1, column=2, padx=5, pady=5, sticky=W)

        self.search_for_fsk = IntVar()
        cbtn_fsk = Checkbutton(master, text="FSK", variable=self.search_for_fsk)
        cbtn_fsk.grid(row=1, column=3, padx=5, pady=5, sticky=W)

        self.search_for_genre = IntVar()
        cbtn_genre = Checkbutton(master, text="Genre", variable=self.search_for_genre)
        cbtn_genre.select()
        cbtn_genre.grid(row=1, column=4, padx=5, pady=5, sticky=W)

        self.search_for_actors = IntVar()
        cbtn_actors = Checkbutton(master, text="Schauspieler", variable=self.search_for_actors)
        cbtn_actors.select()
        cbtn_actors.grid(row=2, column=0, padx=5, pady=5, sticky=W)

        self.search_for_length = IntVar()
        cbtn_length = Checkbutton(master, text="Filmlänge", variable=self.search_for_length)
        cbtn_length.grid(row=2, column=1, padx=5, pady=5, sticky=W)

        self.search_for_comment = IntVar()
        cbtn_comment = Checkbutton(master, text="Kommentare", variable=self.search_for_comment)
        cbtn_comment.select()
        cbtn_comment.grid(row=2, column=2, padx=5, pady=5, sticky=W)

        self.search_for_rating = IntVar()
        cbtn_rating = Checkbutton(master, text="Bewertung", variable=self.search_for_rating)
        cbtn_rating.grid(row=2, column=3, padx=5, pady=5, sticky=W)

        self.search_for_disc_type = IntVar()
        cbtn_disc_type = Checkbutton(master, text="Datenträger", variable=self.search_for_disc_type)
        cbtn_disc_type.grid(row=2, column=4, padx=5, pady=5, sticky=W)

        # display query result

        lbl_res_query = Label(master, text="Suchergebnis", font=("Calibri", "11", "bold"))
        lbl_res_query.grid(row=4, column=0, padx=5, pady=5, sticky=W)

        sb_y = Scrollbar(master)
        sb_y.grid(row=5, column=3, sticky=W+N+S)

        self.lb_res_query = Listbox(master, yscrollcommand=sb_y.set)
        self.lb_res_query.grid(row=5, column=0, padx=5, pady=5, columnspan=3, sticky=W+E)
        self.lb_res_query.bind("<<ListboxSelect>>", self.on_lb_select)

        sb_y.config(command=self.lb_res_query.yview)

        # display details of selected query result

        lbl_title = Label(self.master, text="Filmtitel")
        lbl_title.grid(row=6, column=0, padx=5, sticky=W)

        self.txt_title = StringVar()
        entry_title = Label(self.master, textvariable=self.txt_title)
        entry_title.grid(row=6, column=1, padx=5, columnspan=3, sticky=W)

        lbl_release_year = Label(self.master, text="Veröffentlichungsjahr")
        lbl_release_year.grid(row=7, column=0, padx=5, sticky=W)

        self.txt_release_year = StringVar()
        entry_release_year = Label(self.master, textvariable=self.txt_release_year)
        entry_release_year.grid(row=7, column=1, padx=5, columnspan=3, sticky=W)

        lbl_director = Label(self.master, text="Regisseur")
        lbl_director.grid(row=8, column=0, padx=5, sticky=W)

        self.txt_director = StringVar()
        entry_director = Label(self.master, textvariable=self.txt_director)
        entry_director.grid(row=8, column=1, padx=5, columnspan=3, sticky=W)

        lbl_fsk = Label(self.master, text="FSK")
        lbl_fsk.grid(row=9, column=0, padx=5, sticky=W)

        self.txt_fsk = IntVar()
        entry_fsk = Label(self.master, textvariable=self.txt_fsk)
        entry_fsk.grid(row=9, column=1, padx=5, columnspan=3, sticky=W)

        lbl_genre = Label(self.master, text="Genre")
        lbl_genre.grid(row=10, column=0, padx=5, sticky=W)

        self.txt_genre = StringVar()
        entry_genre = Label(self.master, textvariable=self.txt_genre)
        entry_genre.grid(row=10, column=1, padx=5, columnspan=3, sticky=W)

        lbl_actors = Label(self.master, text="Schauspieler")
        lbl_actors.grid(row=11, column=0, padx=5, sticky=W)

        self.txt_actors = StringVar()
        entry_actors = Label(self.master, textvariable=self.txt_actors)
        entry_actors.grid(row=11, column=1, padx=5, columnspan=5, sticky=W)

        lbl_length = Label(self.master, text="Länge (in Minuten)")
        lbl_length.grid(row=12, column=0, padx=5, sticky=W)

        self.txt_length = IntVar()
        entry_length = Label(self.master, textvariable=self.txt_length)
        entry_length.grid(row=12, column=1, padx=5, columnspan=3, sticky=W)

        lbl_rating = Label(self.master, text="Bewertung (1-5)")
        lbl_rating.grid(row=13, column=0, padx=5, sticky=W)

        self.txt_rating = IntVar()
        entry_rating = Label(self.master, textvariable=self.txt_rating)
        entry_rating.grid(row=13, column=1, padx=5, columnspan=3, sticky=W)

        lbl_disc_type = Label(self.master, text="Datenträgertyp")
        lbl_disc_type.grid(row=14, column=0, padx=5, sticky=W)

        self.txt_disc_type = IntVar()
        entry_disc_type = Label(self.master, textvariable=self.txt_disc_type)
        entry_disc_type.grid(row=14, column=1, padx=5, columnspan=3, sticky=W)

        lbl_comment = Label(self.master, text="Kommentar")
        lbl_comment.grid(row=15, column=0, padx=5, sticky=W)

        self.txt_comment = StringVar()
        entry_comment = Label(self.master, textvariable=self.txt_comment)
        entry_comment.grid(row=15, column=1, columnspan=3, padx=5, sticky=W)

        # show the cover (default is "image not found")
        # resize the cover image
        baseheight = 160
        img = Image.open(self.default_cover)
        hpercent = (baseheight / float(img.size[1]))
        wsize = int((float(img.size[0]) * float(hpercent)))
        img = img.resize((wsize, baseheight), Image.ANTIALIAS)

        image = ImageTk.PhotoImage(img)  # load "no image"-image
        self.lbl_cover = Label(self.master, image=image)
        self.lbl_cover.image = image
        self.lbl_cover.grid(row=5, column=3, sticky=E, columnspan=2)

        # choose db and connect to it
        try:
            self.db_filename_abspath = ""

            if not conf['db_filename_path']:
                # creates frame to choose a database
                frame = Toplevel(master)
                frame.wm_title("Datenbank auswählen")
                frame.transient(master)
                frame.wm_geometry("250x70")
                frame.focus_set()

                btn_new_db = Button(frame, text="Neue Datenbank erstellen", command=lambda: self.start_new_db(frame))
                btn_new_db.pack(padx=5, pady=5, fill=BOTH)

                btn_open_db = Button(frame, text="Datenbank öffnen", command=lambda: self.start_open_db(frame))
                btn_open_db.pack(padx=5, pady=5, fill=BOTH)

                master.wait_window(frame)

                with open(self.SETTINGS_FILE_NAME, 'a') as settings_file:
                    try:  # if path is on other mount than 'C:'
                        db_filename_path = os.path.relpath(self.db_filename_abspath)
                    except ValueError:
                        db_filename_path = self.db_filename_abspath
                    if db_filename_path:
                        settings_file.write("db_filename_path=" + db_filename_path + "\n")
                    else:
                        raise NoDBException()
            else:
                db_filename_path = conf['db_filename_path']

            # enable db connection
            self.db = FilmeDB(db_filename_path)

            db_filename = db_filename_path.split("\\")[-1]
            master.title("Filmdatenbank - " + str(db_filename))

            # show whole database if not empty

            if self.db.get_all():
                self.film_query("")

        except NoDBException:
            messagebox.showerror("Fehler", "keine Datenbank ausgewählt")
        except Exception as e:
            messagebox.showerror("Fehler", "ungültige Datenbank")
            print(type(e))
            print(e)

    def film_query(self, *args):
        """
        search for films which selected (by checkbuttons) attributes contain the text in the search bar
        displays all the results in the listbox
        """
        self.lb_res_query.delete(0, END)

        results = self.db.find_film_filtered(self.query.get(),
                                             title=self.search_for_title.get(), release_year=self.search_for_release_year.get(),
                                             genre=self.search_for_genre.get(), director=self.search_for_director.get(),
                                             fsk=self.search_for_fsk.get(), actors=self.search_for_actors.get(),
                                             length=self.search_for_length.get(), comment=self.search_for_comment.get(),
                                             rating=self.search_for_rating.get(), disc_type=self.search_for_disc_type.get()
                                             )

        for result in results:
            # displays "film_id: title (release_year: director)"
            query_res_str = str(result[0]) + ": " + str(result[1]) + " (" + str(result[2]) + ": " + str(result[3]) + ")"
            self.lb_res_query.insert(END, query_res_str)

        # show details of first result
        self.lb_res_query.activate(0)
        self.display_film(int(self.lb_res_query.get(ACTIVE).split(":")[0]))

    def on_lb_select(self, event):
        """
        handles the selection of an item in the listbox
        """
        w = event.widget
        index = int(w.curselection()[0])
        value = w.get(index)

        self.display_film(int(value.split(":")[0]))

    def display_film(self, film_id):
        """
        displays detailed information about the selected film
        """
        film = self.db.execute_sql("SELECT * FROM films WHERE film_id = %i" % film_id)[0]

        self.txt_title.set(film[1])
        self.txt_release_year.set(film[2] if film[2] is not None else "")
        self.txt_director.set(film[3] if film[3] is not None else "")
        self.txt_fsk.set(film[4] if film[4] is not None else "")
        self.txt_genre.set(film[5] if film[5] is not None else "")
        self.txt_actors.set(film[6] if film[6] is not None else "")
        self.txt_length.set(film[7] if film[7] is not None else "")
        self.txt_comment.set(film[9] if film[9] is not None else "")
        self.txt_rating.set(film[10] if film[10] is not None else "")

        if film[11] == 2:
            self.txt_disc_type.set("DVD")
        elif film[11] == 1:
            self.txt_disc_type.set("BluRay")
        else:
            self.txt_disc_type.set("unbekannt")

        # load image and resize it
        baseheight = 160
        img = Image.open(self.cover_img_dir + film[8]
                         if film[8] is not None
                         else self.default_cover)
        hpercent = (baseheight / float(img.size[1]))
        wsize = int((float(img.size[0]) * float(hpercent)))
        img = img.resize((wsize, baseheight), Image.ANTIALIAS)

        image = ImageTk.PhotoImage(img)
        self.lbl_cover.config(image=image)
        self.lbl_cover.image = image

    def save_db(self):
        """
        saves the database
        """
        try:
            self.db.save_db()
            messagebox.showinfo(message="Speichern erfolgreich.")
        except Exception as e:
            print(e)
            messagebox.showerror("Fehler", "Fehler beim Speichern")

    def export_db(self):
        """
        export the db to a csv file
        """
        try:
            export_filename = filedialog.asksaveasfilename(initialdir=self.private_db_dir,
                                                           defaultextension=".csv",
                                                           filetypes=[(".csv-Datei", "*.csv")],
                                                           title="Exportieren als")
            if export_filename and export_filename.split(".")[-1] == "csv":
                self.db.export_db(export_filename)
                messagebox.showinfo(message="Datei erfolgreich exportiert.")
            else:
                raise DBExportException()
        except DBExportException:
            messagebox.showerror("Fehler", "ungültiger Dateiname")
        except Exception as e:
            messagebox.showerror("Fehler", "Fehler beim Exportieren")
            print(e)

    def import_db(self):
        """
        imports data a a csv file to the current database
        !careful: overwrites the data of the database!
        """
        try:
            import_filename = filedialog.askopenfilename(initialdir=self.private_db_dir,
                                                         filetypes=[("csv-Datei", "*.csv")],
                                                         title="Datenbank importieren")
            if import_filename and import_filename.split(".")[-1] == "csv":
                if messagebox.askokcancel("Warnung",
                                          "Beim Importieren werden eventuell Daten überschrieben. Fortfahren?"):
                    self.db.import_db(import_filename)
                    messagebox.showinfo(message="Datei erfolgreich importiert.")
                else:
                    messagebox.showerror(message="Import abgebrochen")
            else:
                raise DBImportException()
        except DBImportException:
            messagebox.showerror("Fehlerwarnung", "ungültige Datei")
        except Exception as e:
            messagebox.showerror("Fehlerwarnung", "Fehler beim Importieren")
            print(e)

    def change_db(self, create_new=False):
        """
        change the database to display/work with
        :param create_new: if True: create a new database file
        """

        # save old database
        if messagebox.askyesno("Speichern", "Aktuelle Datenbank vor dem Wechsel speichern?"):
            self.save_db()
        try:

            if create_new:
                # new db-file
                db_filename_abspath = filedialog.asksaveasfilename(title="Speichern unter",
                                                                   initialdir=self.private_db_dir,
                                                                   defaultextension=".db",
                                                                   filetypes=[("Datenbank", "*.db")])
            else:
                # open db-file
                db_filename_abspath = filedialog.askopenfilename(initialdir=self.private_db_dir,
                                                                 filetypes=[("Datenbank", "*.db")],
                                                                 title="Datenbank auswählen")

            with open(self.SETTINGS_FILE_NAME, 'r+') as settings_file:
                if db_filename_abspath:
                    try:  # if path is on other mount than 'C:'
                        db_filename_path = os.path.relpath(db_filename_abspath)
                    except ValueError:
                        db_filename_path = db_filename_abspath
                    # rewrites the standard
                    text = settings_file.readlines()
                    settings_file.seek(0)
                    for line in text:
                        if not line.startswith("db_filename_path"):
                            settings_file.write(line)
                        else:
                            settings_file.write("db_filename_path=" + db_filename_path + "\n")
                    settings_file.truncate()
                else:
                    raise NoDBException()

            # connect to new database
            self.db = FilmeDB(db_filename_path)
            db_filename = db_filename_path.split("\\")[-1]
            self.master.title("Filmdatenbank - " + str(db_filename))
        except NoDBException:
            messagebox.showerror("Fehler", "keine Datenbank ausgewählt")
        except Exception as e:
            messagebox.showerror("Fehler", "ungültige Datenbank")
            print(type(e))
            print(e)

        if self.db.get_all():
            self.film_query("")

            # select first film
            self.lb_res_query.activate(0)
            self.display_film(int(self.lb_res_query.get(ACTIVE).split(":")[0]))

    def start_new_db(self, start_toplevel):
        """
        create new database and store path it in variable
        :param start_toplevel: toplevel frame which asks for database if no standard is stored
        """
        db_path = filedialog.asksaveasfilename(title="Speichern unter",
                                               initialdir=self.private_db_dir,
                                               defaultextension=".db",
                                               filetypes=[("Datenbank", "*.db")])
        if db_path:
            self.db_filename_abspath = db_path
            start_toplevel.destroy()
        else:
            raise NoDBException()

    def start_open_db(self, toplevel):
        """
        open new database and store path it in variable
        :param start_toplevel: toplevel frame which asks for database if no standard is stored
        """
        db_path = filedialog.askopenfilename(initialdir=self.private_db_dir,
                                             filetypes=[("Datenbank", "*.db")],
                                             title="Datenbank auswählen")
        if db_path:
            self.db_filename_abspath = db_path
            toplevel.destroy()
        else:
            raise NoDBException()

    def on_closing(self):
        """
        ask to save the database on closing the window
        """
        save = messagebox.askyesnocancel("Speichern beim Verlassen", "Aktuelle Datenbank speichern?")

        if save:
            self.save_db()
            self.master.destroy()
        elif save is None:
            pass
        else:
            self.master.destroy()

    @staticmethod
    def load_settings():
        # check if standard database is stored
        conf = {}
        # assign default values
        conf['db_filename_path'] = ""
        conf['cover_img_dir'] = DB_GUI.STANDARD_COVER_IMG_DIR
        conf['private_db_dir'] = DB_GUI.STANDARD_DB_DIR
        conf['default_cover'] = DB_GUI.STANDARD_IMG_COVER
        conf['online_db'] = DB_GUI.STANDARD_ONLINE_DB
        conf['translate_genres'] = True
        conf['default_disc_type'] = DB_GUI.STANDARD_DISC_TYPE
        if os.path.isfile(DB_GUI.SETTINGS_FILE_NAME):
            with open(DB_GUI.SETTINGS_FILE_NAME, 'r') as settings_file:
                for line in settings_file:
                    if line.startswith("db_filename_path"):  # selected database
                        db_filename_path = line.split("=")[1]
                        conf['db_filename_path'] = db_filename_path[:-1]
                    elif line.startswith("cover_directory"):  # where database data is stored
                        cover_img_dir = line.split("=")[1]
                        conf['cover_img_dir'] = cover_img_dir[:-1]
                    elif line.startswith("private_db_directory"):
                        private_db_dir = line.split("=")[1]
                        conf['private_db_dir'] = private_db_dir[:-1]
                    elif line.startswith("default_cover"):
                        default_cover = line.split('=')[1]
                        conf['default_cover'] = default_cover[:-1]
                    elif line.startswith("online_db"):
                        online_db = line.split('=')[1]
                        conf['online_db'] = online_db[:-1]
                    elif line.startswith('translate_genres'):
                        translate_genres = line.split('=')[1]
                        conf['translate_genres'] = translate_genres[:-1]
                    elif line.startswith('default_disc_type'):
                        default_disc_type = line.split('=')[1]
                        conf['default_disc_type'] = default_disc_type[:-1]
        return conf


class WindowFilmEdit:

    def __init__(self, db_gui, db, edit_type='add'):
        self.db = db
        self.db_gui = db_gui

        self.frame = Toplevel()
        self.frame.transient(self.db_gui.master)

        # entries for the film data
        lbl_title = Label(self.frame, text="Filmtitel")
        lbl_title.grid(row=0, column=0, padx=5, pady=5, sticky=W)

        if edit_type in ['add', 'edit']:
            btn_load_film_data = Button(self.frame, text="laden",
                                        command=lambda: self.load_film_data(self.db_gui.default_online_db,
                                                                            self.db_gui.translate_genres))
            btn_load_film_data.grid(row=0, column=0, pady=5, padx=5, sticky=E)

        self.txt_title = StringVar()

        entry_title = Entry(self.frame, width=20, textvariable=self.txt_title)
        entry_title.grid(row=1, column=0, padx=5)

        lbl_release_year = Label(self.frame, text="Veröffentlichungsjahr")
        lbl_release_year.grid(row=0, column=1, padx=5, pady=5, sticky=W)

        self.txt_release_year = StringVar()

        entry_release_year = Entry(self.frame, width=20, textvariable=self.txt_release_year)
        entry_release_year.grid(row=1, column=1, padx=5)

        lbl_director = Label(self.frame, text="Regisseur")
        lbl_director.grid(row=0, column=2, padx=5, pady=5, sticky=W)

        self.txt_director = StringVar()

        entry_director = Entry(self.frame, width=20, textvariable=self.txt_director)
        entry_director.grid(row=1, column=2, padx=5)

        lbl_fsk = Label(self.frame, text="FSK")
        lbl_fsk.grid(row=0, column=3, padx=5, pady=5, sticky=W)

        self.txt_fsk = StringVar()

        entry_fsk = Entry(self.frame, width=20, textvariable=self.txt_fsk)
        entry_fsk.grid(row=1, column=3, padx=5)

        lbl_genre = Label(self.frame, text="Genre")
        lbl_genre.grid(row=0, column=4, padx=5, pady=5, sticky=W)

        self.txt_genre = StringVar()

        entry_genre = Entry(self.frame, width=20, textvariable=self.txt_genre)
        entry_genre.grid(row=1, column=4, padx=5)

        lbl_actors = Label(self.frame, text="Schauspieler")
        lbl_actors.grid(row=2, column=0, padx=5, pady=5, sticky=W)

        self.txt_actors = StringVar()

        entry_actors = Entry(self.frame, width=20, textvariable=self.txt_actors)
        entry_actors.grid(row=3, column=0, padx=5)

        lbl_length = Label(self.frame, text="Länge (in Minuten)")
        lbl_length.grid(row=2, column=1, padx=5, pady=5, sticky=W)

        self.txt_length = StringVar()

        entry_length = Entry(self.frame, width=20, textvariable=self.txt_length)
        entry_length.grid(row=3, column=1, padx=5)

        lbl_rating = Label(self.frame, text="Bewertung (1-5)")
        lbl_rating.grid(row=2, column=3, padx=5, pady=5, sticky=W)

        self.txt_rating = StringVar()

        entry_rating = Entry(self.frame, width=5, textvariable=self.txt_rating)
        entry_rating.grid(row=2, column=4, sticky=E, padx=5)

        lbl_disc_type = Label(self.frame, text="Datenträgertyp (0=?, 1=BluRay, 2=DVD)")
        lbl_disc_type.grid(row=3, column=3, padx=5, columnspan=2, sticky=W)

        self.txt_disc_type = StringVar()

        entry_disc_type = Entry(self.frame, width=5, textvariable=self.txt_disc_type)
        entry_disc_type.grid(row=3, column=4, sticky=E, padx=5)

        lbl_cover_path = Label(self.frame, text="Coverpfad")
        lbl_cover_path.grid(row=2, column=2, padx=5, pady=5, sticky=W)

        btn_cover_path = Button(self.frame, text="wählen", command=self.load_cover_path)
        btn_cover_path.grid(row=2, column=2, pady=5, padx=5, sticky=E)

        self.txt_cover_path = StringVar()

        entry_cover_path = Entry(self.frame, width=20, textvariable=self.txt_cover_path)
        entry_cover_path.grid(row=3, column=2, padx=5)

        lbl_comment = Label(self.frame, text="Kommentar")
        lbl_comment.grid(row=4, column=0, padx=5, pady=5, sticky=W)

        self.txt_comment = StringVar()

        entry_comment = Entry(self.frame, textvariable=self.txt_comment)
        entry_comment.grid(row=4, column=1, columnspan=2, padx=5, sticky=W+E)

        # confirm button

        if edit_type is 'add':
            self.txt_disc_type.set(str(self.db_gui.default_disc_type))
            txt_btn_confirm = "Film hinzufügen"
        elif edit_type is 'edit':
            txt_btn_confirm = "Änderungen speichern"
        elif edit_type is 'remove':
            txt_btn_confirm = "Film löschen"

        self.btn_confirm = Button(self.frame, text=txt_btn_confirm, width=20, command=lambda: self.confirm_edit(edit_type))
        self.btn_confirm.grid(row=4, column=3, padx=5, pady=10, columnspan=2, sticky=W)

        if edit_type is 'add':
            new_film_id = self.db.execute_sql("SELECT MAX(film_id) from films")[0][0] + 1
            self.frame_title = "Film hinzufügen - Nummer " + str(new_film_id)
        elif edit_type is 'edit':
            self.frame_title = "Film bearbeiten"
        elif edit_type is 'remove':
            self.frame_title = "Film löschen"
        self.frame.geometry("700x150")

        if edit_type is 'edit' or edit_type is 'remove':
            # store film_id to edit/delete the film
            self.edit_film_id = 0
            WindowLoadFilm(self, self.db)
        else:
            self.set_frame_title()

        self.db_gui.master.wait_window(self.frame)

    def set_frame_title(self):
        self.frame.title(self.frame_title)

    def load_cover_path(self):
        cover_path = filedialog.askopenfilename(initialdir=self.db_gui.private_db_dir,
                                                filetypes=[("Bilddatei", "*.jpg *.png *.gif"), ("alle Dateien", "*.*")],
                                                title="Coverbild auswählen")
        cover_relpath = os.path.relpath(cover_path)
        self.txt_cover_path.set(cover_relpath)

    def load_film_data(self, database='imdb', translate_genre=True):

        def _translate_genre(genre):
            translations = {
                'Adventure': 'Abenteuer',
                'Animation': 'Animation',
                'Comedy': 'Komödie',
                'Crime': 'Krimi',
                'Documentary': 'Dokumentation',
                'Family': 'Familie',
                'Romance': 'Romantik',
                'Sci-Fi': 'Science-Fiction',
                'Short': 'Kurzfilm',
                'War': 'Kriegsfilm'
            }
            return translations[genre] if genre in translations else genre

        def load_film_data_from_omdb(edit_window, film_title, translate_genre):

            # get the film data in JSON format
            json_data = OmdbFilmImport.get_film_json(film_title)

            # display th film data
            edit_window.txt_title.set(json_data['Title'])
            edit_window.txt_release_year.set(json_data['Year'])
            edit_window.txt_director.set(json_data['Director'])
            edit_window.txt_fsk.set("")
            if translate_genre:
                genres = []
                for genre in json_data['Genre'].split(', '):
                    genres.append(_translate_genre(genre))
                edit_window.txt_genre.set(', '.join(genres))
            else:
                edit_window.txt_genre.set(json_data['Genre'])
            edit_window.txt_actors.set(json_data['Actors'])
            edit_window.txt_length.set(json_data['Runtime'].split(' ')[0])
            edit_window.txt_cover_path.set(json_data['Poster'])

        def load_film_data_from_imdb(edit_window, film_title, translate_genre):

            film_data = ImdbFilmImport.get_film_by_title(film_title)

            if film_data['German title']:
                edit_window.txt_title.set(film_data['German title'])
            else:
                edit_window.txt_title.set(film_data['original title'])
            edit_window.txt_release_year.set(film_data['year'])
            edit_window.txt_director.set(film_data['director'])
            edit_window.txt_fsk.set(film_data['fsk'])
            if translate_genre:
                genres = []
                for genre in film_data['genre'].split(', '):
                    genres.append(_translate_genre(genre))
                edit_window.txt_genre.set(', '.join(genres))
            else:
                edit_window.txt_genre.set(film_data['genre'])
            edit_window.txt_actors.set(film_data['cast'])
            edit_window.txt_length.set(film_data['length'])
            edit_window.txt_cover_path.set(film_data['cover_url'])

        try:
            # check whether title field is empty
            if self.txt_title.get():
                title = self.txt_title.get()
            else:
                raise NoTitleEnteredException()

            # display film data
            if database == 'imdb':
                load_film_data_from_imdb(self, title, translate_genre)
            elif database == 'omdb':
                load_film_data_from_omdb(self, title, translate_genre)
        except NoTitleEnteredException:
            messagebox.showerror("Fehler", "Filmtitel fehlt")
        except MovieNotFoundException:
            messagebox.showerror("Fehler", "Kein Film mit diesem Titel gefunden")
        except FilmImportException:
            messagebox.showerror("Fehler", "Fehler beim Importieren der Filmdaten")
        except Exception as e:
            messagebox.showerror("Fehler", "Fehler")
            print(e)

    def confirm_edit(self, action):
        if action is 'add':
            try:
                self.add_film()
                self.frame.destroy()
                messagebox.showinfo(message="Film erfolgreich hinzugefügt")
            except FilmAddException as fae:
                messagebox.showerror("Fehler", "fehlende Eingabe")
            except CoverNotAnImageException:
                messagebox.showerror("Fehler", "URL verweist auf keine Bilddatei")
            except CoverDownloadException:
                messagebox.showerror("Fehler", "Fehler beim Download der Coverdatei")
            except Exception as e:
                messagebox.showerror("Fehler", "Fehler")
                print(e)
        elif action is 'edit':
            try:
                self.edit_film()
                self.frame.destroy()
                messagebox.showinfo(message="Film erfolgreich bearbeitet")
            except FilmEditException:
                messagebox.showerror("Fehler", "fehlende Eingabe")
            except CoverNotAnImageException:
                messagebox.showerror("Fehler", "URL verweist auf keine Bilddatei")
            except CoverDownloadException:
                messagebox.showerror("Fehler", "Fehler beim Download der Coverdatei")
            except Exception as e:
                messagebox.showerror("Fehler", "Fehler")
                print(e)
        elif action is 'remove':
            try:
                if messagebox.askokcancel("Film löschen", "Film wirklich löschen?"):
                    self.remove_film()
                    self.frame.destroy()
                else:
                    raise FilmRemoveException()
            except FilmRemoveException:
                messagebox.showwarning(message="Löschen abgebrochen")
                self.frame.destroy()
            except Exception as e:
                messagebox.showerror("Fehler", "Fehler beim Löschen")
                print(e)

        self.db_gui.film_query()

    def add_film(self):
        if self.txt_title.get():
            title = self.txt_title.get()
        else:
            raise FilmAddException()

        release_year = int(self.txt_release_year.get()) if self.txt_release_year.get() != "" else None
        director = self.txt_director.get() if self.txt_director.get() != "" else None
        fsk = int(self.txt_fsk.get()) if self.txt_fsk.get() != "" else None
        genre = self.txt_genre.get() if self.txt_genre.get() != "" else None
        actors = self.txt_actors.get() if self.txt_actors.get() != "" else None
        length = int(self.txt_length.get()) if self.txt_length.get() != "" else None
        comment = self.txt_comment.get() if self.txt_comment.get() != "" else None
        rating = int(self.txt_rating.get()) if self.txt_rating.get() != "" else None
        disc_type = int(self.txt_disc_type.get()) if self.txt_disc_type.get() != "" else None

        cover_path = self.txt_cover_path.get() if self.txt_cover_path.get() != "" else None
        if cover_path:
            # if cover_path refers to a link on the internet download that cover picture from link
            if "www" in cover_path or cover_path.startswith("http"):
                cover_path = self.download_cover_picture(film_title=title, cover_path=cover_path)
            # if cover is in default directory remove it
            if self.db_gui.cover_img_dir in cover_path:
                cover_path = cover_path.split(self.db_gui.cover_img_dir)[1]
            print(cover_path)

        self.db.add_film(Film(title, release_year, director, fsk, genre, actors,
                         length, cover_path, comment, rating, disc_type))

        print("film added")

    def edit_film(self):
        if self.txt_title.get():
            title = self.txt_title.get()
        else:
            raise FilmAddException()

        release_year = int(self.txt_release_year.get()) if self.txt_release_year.get() != "" else None
        director = self.txt_director.get() if self.txt_director.get() != "" else None
        fsk = int(self.txt_fsk.get()) if self.txt_fsk.get() != "" else None
        genre = self.txt_genre.get() if self.txt_genre.get() != "" else None
        actors = self.txt_actors.get() if self.txt_actors.get() != "" else None
        length = int(self.txt_length.get()) if self.txt_length.get() != "" else None
        comment = self.txt_comment.get() if self.txt_comment.get() != "" else None
        rating = int(self.txt_rating.get()) if self.txt_rating.get() != "" else None
        disc_type = int(self.txt_disc_type.get()) if self.txt_disc_type.get() != "" else None

        cover_path = self.txt_cover_path.get() if self.txt_cover_path.get() != "" else None
        if cover_path:
            # if cover_path refers to a link on the internet download that cover picture from link
            if "www" in cover_path or cover_path.startswith("http"):
                cover_path = self.download_cover_picture(film_title=title, cover_path=cover_path)
            # if cover is in default directory remove it
            if self.db_gui.cover_img_dir in cover_path:
                cover_path = cover_path.split(self.db_gui.cover_img_dir)[1]

        self.db.edit_film_by_id(self.edit_film_id, [title, release_year, director, fsk, genre, actors,
                                                    length, cover_path, comment, rating, disc_type])

        print("film edited")

    def remove_film(self):
        self.db.remove_film_by_id(self.edit_film_id)
        print("film removed")

    def on_closing(self):
        pass

    @staticmethod
    def download_cover_picture(film_title, cover_path):
        """ download the picture from the internet
            :return path to the picture """

        if cover_path.endswith(".jpg") or cover_path.endswith(".png") or cover_path.endswith(".gif") or cover_path.endswith('.jfif'):
            r = requests.get(cover_path, stream=True)

            if r.status_code == 200:

                # create the image name from film title
                img_name = []
                for char in film_title:
                    if not char == ":":
                        img_name.append(char)
                img_name = "".join(img_name) + "." + cover_path.split(".")[-1]

                # create the path to the storage
                conf = DB_GUI.load_settings()
                cover_img_dir = conf['cover_img_dir'] if conf['cover_img_dir'] else DB_GUI.STANDARD_COVER_IMG_DIR
                store_path = os.path.join(cover_img_dir, img_name)

                with open(store_path, 'wb') as f:
                    for chunk in r:
                        f.write(chunk)

                # return the path to the picture
                return store_path
            else:
                raise CoverDownloadException()
        else:
            raise CoverNotAnImageException()


class WindowLoadFilm:

    def __init__(self, window_film_edit, db):
        self.window_film_edit = window_film_edit

        self.frame = Toplevel()
        self.frame.title("Film auswählen")
        self.frame.transient(window_film_edit.frame)

        self.frame.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.db = db

        lbl = Label(self.frame, text="Film auswählen")
        lbl.grid(sticky=W, padx=5)

        sb_y = Scrollbar(self.frame)
        sb_y.grid(row=1, column=1, sticky=N+S+W)

        self.lb = Listbox(self.frame, yscrollcommand=sb_y.set)
        self.lb.grid(row=1, sticky=W+E, padx=5)

        sb_y.config(command=self.lb.yview)

        btn_confirm = Button(self.frame, text="ausgewählten Film bearbeiten",
                             command=lambda: self.send_film_to_edit(window_film_edit, self.lb.get(ACTIVE)))
        btn_confirm.grid(row=2, columnspan=2, padx=5, pady=5)

        self.load_films()
        window_film_edit.frame.wait_window(self.frame)

    def load_films(self):
        sql_command = """
            SELECT film_id, title
            FROM films
            """
        for film in self.db.execute_sql(sql_command):
            result_str = str(film[0]) + ": " + film[1]
            self.lb.insert(END, result_str)

    def send_film_to_edit(self, window_film_edit, selected_film):
        if not selected_film:
            messagebox.showerror("Fehler", "kein Film ausgeählt")
        else:
            film = self.db.get_film_by_id(int(selected_film.split(":")[0]))

            window_film_edit.edit_film_id = int(film[0])

            window_film_edit.txt_title.set(film[1])
            window_film_edit.txt_release_year.set(film[2] if film[2] is not None else "")
            window_film_edit.txt_director.set(film[3] if film[3] is not None else "")
            window_film_edit.txt_fsk.set(film[4] if film[4] is not None else "")
            window_film_edit.txt_genre.set(film[5] if film[5] is not None else "")
            window_film_edit.txt_actors.set(film[6] if film[6] is not None else "")
            window_film_edit.txt_length.set(film[7] if film[7] is not None else "")
            window_film_edit.txt_cover_path.set(film[8] if film[8] is not None else "")
            window_film_edit.txt_comment.set(film[9] if film[9] is not None else "")
            window_film_edit.txt_rating.set(film[10] if film[10] is not None else "")
            window_film_edit.txt_disc_type.set(film[11] if film[11] is not None else "")

            window_film_edit.frame_title += " - Nummer " + str(window_film_edit.edit_film_id)
            window_film_edit.set_frame_title()

            self.frame.destroy()

    def on_closing(self):
        self.send_film_to_edit(self.window_film_edit, self.lb.get(ACTIVE))
        self.frame.destroy()


class NoTitleEnteredException(Exception):
    pass


class FilmAddException(Exception):
    pass


class FilmEditException(Exception):
    pass


class FilmRemoveException(Exception):
    pass


class CoverException(Exception):
    pass


class CoverInWrongDirectoryException(CoverException):
    pass


class CoverDownloadException(CoverException):
    pass


class CoverNotAnImageException(CoverDownloadException):
    pass

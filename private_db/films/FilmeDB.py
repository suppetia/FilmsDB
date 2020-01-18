import sqlite3
import csv


class Film:

    def __init__(self, title, release_year=None, director=None, fsk=None, genre=None, actors=None, length=None,
                 cover_path=None, comment=None, rating=None, disc_type=None):
        """
        :param title: String
        :param release_year: Integer
        :param director: String
        :param fsk: Integer
        :param genre: String
        :param actors: String
        :param length: String
        :param cover_path: String
        :param comment: String
        :param rating: Integer
        :param disc_type: Integer - 0=unknown, 1=BluRay, 2=DVD
        """
        self.data = [title, release_year, director, fsk, genre, actors, length, cover_path,
                     comment, rating, disc_type]
        if disc_type is None:
            self.data[-1] = 0


class FilmeDB:

    def __init__(self, name):
        # connecting to database
        self.connection = sqlite3.connect(name)
        cursor = self.connection.cursor()

        first_command = """
            CREATE TABLE if not exists films (
            film_id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            release_year INTEGER,
            director TEXT,
            fsk INTEGER,
            genre TEXT,
            actors TEXT,
            length INTEGER,
            cover_path TEXT,
            comment TEXT,
            rating INTEGER,
            disc_type INTEGER NOT NULL
            )
            """

        cursor.execute(first_command)

    def __del__(self):
        self.connection.close()

    def save_db(self):
        self.connection.commit()

    def add_film(self, film):
        insert_data = """
        INSERT INTO films 
        VALUES(NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) """

        cursor = self.connection.cursor()
        cursor.execute(insert_data, film.data)

    def add_raw_film_with_id(self, film_data):
        insert_data = """
        INSERT INTO films 
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) """

        cursor = self.connection.cursor()
        cursor.execute(insert_data, film_data)

    def execute_sql(self, command):
        cursor = self.connection.cursor()
        cursor.execute(command)

        return cursor.fetchall()

    def get_all(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM films")

        return cursor.fetchall()

    def get_film_by_id(self, search):
        cursor = self.connection.cursor()
        sql_search = str("SELECT * FROM films WHERE film_id = %i" % search)
        cursor.execute(sql_search)

        return cursor.fetchone()

    def find_film_by_title(self, search):
        cursor = self.connection.cursor()
        sql_search = str("SELECT * FROM films WHERE title LIKE '%" + search + "%'")
        cursor.execute(sql_search)

        return cursor.fetchall()

    def find_film_by_release_year(self, search):
        cursor = self.connection.cursor()
        sql_search = str("SELECT * FROM films WHERE release_year LIKE '%" + search + "%'")
        cursor.execute(sql_search)

        return cursor.fetchall()

    def find_film_by_genre(self, search):
        cursor = self.connection.cursor()
        sql_search = str("SELECT * FROM films WHERE genre LIKE '%" + search + "%'")
        cursor.execute(sql_search)

        return cursor.fetchall()

    def find_film_by_director(self, search):
        cursor = self.connection.cursor()
        sql_search = str("SELECT * FROM films WHERE director LIKE '%" + search + "%'")
        cursor.execute(sql_search)

        return cursor.fetchall()

    def find_film_by_fsk(self, search):
        cursor = self.connection.cursor()
        sql_search = str("SELECT * FROM films WHERE fsk LIKE '" + search + "'")
        cursor.execute(sql_search)

        return cursor.fetchall()

    def find_film_by_actors(self, search):
        cursor = self.connection.cursor()
        sql_search = str("SELECT * FROM films WHERE actors LIKE '%" + search + "%'")
        cursor.execute(sql_search)

        return cursor.fetchall()

    def find_film_by_length(self, search):
        cursor = self.connection.cursor()
        sql_search = str("SELECT * FROM films WHERE length LIKE '" + search + "'")
        cursor.execute(sql_search)

        return cursor.fetchall()

    def find_film_by_comment(self, search):
        cursor = self.connection.cursor()
        sql_search = str("SELECT * FROM films WHERE comment LIKE '%" + search + "%'")
        cursor.execute(sql_search)

        return cursor.fetchall()

    def find_film_by_rating(self, search):
        cursor = self.connection.cursor()
        sql_search = str("SELECT * FROM films WHERE rating LIKE '" + search + "'")
        cursor.execute(sql_search)

        return cursor.fetchall()

    def find_film_by_disc_type(self, search):
        cursor = self.connection.cursor()
        sql_search = str("SELECT * FROM films WHERE disc_type LIKE '" + search + "'")
        cursor.execute(sql_search)

        return cursor.fetchall()

    def find_film(self, search):
        results = []
        results.append(self.find_film_by_title(search))
        results.append(self.find_film_by_release_year(search))
        results.append(self.find_film_by_genre(search))
        results.append(self.find_film_by_director(search))
        results.append(self.find_film_by_actors(search))

        search_result = []
        for result in results:
            for single_result in result:
                search_result.append(single_result)

        result = list(set(search_result))
        result.sort()

        return result

    def find_film_filtered(self, search, title, release_year, director, fsk, genre, actors, length,
                           comment, rating, disc_type):
        results = []
        if title:
            results.append(self.find_film_by_title(search))
        if release_year:
            results.append(self.find_film_by_release_year(search))
        if genre:
            results.append(self.find_film_by_genre(search))
        if director:
            results.append(self.find_film_by_director(search))
        if fsk:
            results.append(self.find_film_by_fsk(search))
        if actors:
            results.append(self.find_film_by_actors(search))
        if length:
            results.append(self.find_film_by_length(search))
        if comment:
            results.append(self.find_film_by_comment(search))
        if rating:
            results.append(self.find_film_by_rating(search))
        if disc_type:
            results.append(self.find_film_by_disc_type(search))

        search_result = []
        for result in results:
            for single_result in result:
                search_result.append(single_result)

        result = list(set(search_result))
        result.sort()

        return result

    def remove_film_by_id(self, film_id):
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM films WHERE film_id = %i" % film_id)

    def remove_film_by_title(self, title):
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM films WHERE title = '%s'" % title)

    def edit_film_by_id(self, film_id, data):
        update_data = """
        UPDATE films SET 
        title = ?,
        release_year = ?,
        director = ?,
        fsk = ?,
        genre = ?,
        actors = ?,
        length = ?,
        cover_path = ?,
        comment = ?,
        rating = ?,
        disc_type = ?    
        WHERE film_id = %i """ % film_id
        cursor = self.connection.cursor()
        cursor.execute(update_data, data)

    def export_db(self, filename):
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ["film_id", "title", "release_year", "director", "fsk", "genre", "actors", "length",
                          "cover_path", "comment", "rating", "disc_type"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for film in self.get_all():
                writer.writerow(dict(zip(fieldnames, film)))

    def import_db(self, filename):
        with open(filename, newline='') as csvfile:
            dialect = csv.Sniffer().sniff(csvfile.read(1024))
            csvfile.seek(0)
            reader = csv.DictReader(csvfile, dialect=dialect)
            for row in reader:
                data = []
                for (key, value) in row.items():
                    if key is "film_id":
                        if value:
                            data.append(int(value))
                        else:
                            raise FilmIDException()
                    elif key in ["release_year", "fsk", "length", "rating", "disc_type"]:
                        data.append(int(value) if value else None)
                    else:
                        data.append(value if value else None)

                if self.get_film_by_id(int(data[0])):
                    self.remove_film_by_id(int(data[0]))
                self.add_raw_film_with_id(data)


class FilmIDException(Exception):
    pass


class NoDBException(Exception):
    pass


class DBImportException(Exception):
    pass


class DBExportException(Exception):
    pass

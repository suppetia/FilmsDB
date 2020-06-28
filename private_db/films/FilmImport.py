import requests
import imdb

from private_db.films.credentials import omdb_api_key, google_api_key
from private_db.films.BarcodeScanner import scan_camera_input


class OmdbFilmImport:

    omdb_url = "http://www.omdbapi.com/"
    api_key = omdb_api_key

    @staticmethod
    def get_film_json(title, full_plot=True):
        """ get the json data of a film from 'OpenMovieDataBase' by searching for the title """

        # exchange ' ' with '+' for url
        title_list = list(title)
        for i in range(len(title_list)):
            if title_list[i] == " ":
                title_list[i] = "+"
        title = "".join(title_list)

        # create the request url
        if full_plot:
            req_url = OmdbFilmImport.omdb_url + "?t=" + title + "&plot=full" + "&apikey=" + OmdbFilmImport.api_key
        else:
            req_url = OmdbFilmImport.omdb_url + "?t=" + title + "&apikey=" + OmdbFilmImport.api_key

        # make a url request to the filmdatabase-api and return the json data
        req = requests.get(req_url)
        req_json = req.json()

        if req_json['Response'] == "True":
            return req_json
        else:
            if req_json['Error'] == "Movie not found!":
                raise MovieNotFoundException()
            else:
                raise FilmImportException()


class ImdbFilmImport:

    @staticmethod
    def get_film_by_title(title):

        film_data = {}

        try:
            ia = imdb.IMDb()

            movies = ia.search_movie(title)
            if not movies:
                raise MovieNotFoundException()
            movie = ia.get_movie(movies[0].movieID)

            film_data['original title'] = movie.get('title')
            film_data['German title'] = None
            for i in movie.get('akas'):
                if i.endswith('(Germany)'):
                    film_data['German title'] = i[:-10]
                    break
            film_data['year'] = movie.get('year')

            # TODO: test runtimes
            try:
                film_data['length'] = int(movie.get('runtimes')[0]) if movie.get('runtimes') else ""
            except ValueError:
                print(movie.get('runtimes'))
                for x in movie.get('runtimes'):
                    if x.startswith('GER'):
                        film_data['length'] = x.split(':')[1]
            if movie.get('certificates'):
                for x in movie.get('certificates'):
                    if x.startswith('Germany'):
                        film_data['fsk'] = x.split(':')[1]
                        break
                if not 'fsk' in film_data:
                    film_data['fsk'] = ""
            else:
                film_data['fsk'] = ""

            film_data['director'] = ', '.join([x['name'] for x in movie.get('director')]) if movie.get('director') else ""
            film_data['genre'] = ', '.join([x for x in movie.get('genre')]) if movie.get('genre') else ""
            film_data['cast'] = ', '.join([x['name'] for x in movie.get('cast')[:5]]) if movie.get('cast') else ""
            film_data['cover_url'] = movie.get('cover url') if movie.get('cover url') else ""

            return film_data
        except imdb.IMDbError as e:
            print(e)
            raise FilmImportException()
        except Exception as e:
            print(e)
            raise FilmImportException()


class BarcodeFilmImport:
    """
    1. scan a barcode
    2. use google module to find the film title
    """

    @staticmethod
    def read_barcode_and_get_title():
        def _get_title_by_barcode(barcode_data):
            cse_id = "002812416261647450282:1eskzvbjb3e"
            api_key = google_api_key

            query = barcode_data
            start = 1
            url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={cse_id}&q={query}&start={start}"

            data = requests.get(url).json()
            # get the result items
            search_items = data.get("items")

            if search_items:
                # as the result uses 'buecher.de' this refers to the title of the page
                return search_items[0].get("title").split("auf DVD")[0]
            else:
                raise FilmImportException()

        barcode_data = scan_camera_input()
        title = _get_title_by_barcode(barcode_data)

        return title


class FilmImportException(Exception):
    pass


class MovieNotFoundException(FilmImportException):
    pass


class BarcodeScanException(Exception):
    pass

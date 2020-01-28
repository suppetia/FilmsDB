import requests
import imdb


class OmdbFilmImport:

    omdb_url = "http://www.omdbapi.com/"
    api_key = "2373902e"

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
                film_data['length'] = int(movie.get('runtimes')[0])
            except ValueError:
                print(movie.get('runtimes'))
                for x in movie.get('runtimes'):
                    if x.startswith('GER'):
                        film_data['length'] = x.split(':')[1]
            film_data['director'] = ', '.join([x['name'] for x in movie.get('director')])
            film_data['genre'] = ', '.join([x for x in movie.get('genre')])
            film_data['cast'] = ', '.join([x['name'] for x in movie.get('cast')[:5]])
            film_data['cover_url'] = movie.get('cover url')

            return film_data
        except imdb.IMDbError as e:
            print(e)
            raise FilmImportException()
        except Exception as e:
            print(e)
            raise FilmImportException()


class FilmImportException(Exception):
    pass


class MovieNotFoundException(FilmImportException):
    pass

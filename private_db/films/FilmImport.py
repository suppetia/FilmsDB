import requests


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


class FilmImportException(Exception):
    pass


class MovieNotFoundException(FilmImportException):
    pass

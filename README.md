# movie database gui
--- German project ---

Store your films in a database and find them by querying for film attributes.

## User Manual

- run 'db_main.py'
- select database file or create a new one
    - *hint*: you can change the database by clicking 
        >(menubar) 'Datei' > 'Datenbank öffnen' 
    
        or create a new one by clicking 
        >(menubar) 'Filme' > 'Film hinzufügen'


- add films by clicking 
    >(menubar) 'Filme' > 'Film hinzufügen'
    - *hint*: click 'laden' after entering the title to get some data from OMDB 
    
            cover picture will be download if you leave the internet link
            
- edit films by clicking 
    >(menubar) 'Filme' > 'Film bearbeiten'
    
    and choosing the film you want to edit in the pop-up window
    
- remove films by clicking 
    >(menubar) 'Filme' > 'Film hinzufügen'
    
    and choosing the film you want to remove in the pop-up window
    
    -> confirm after checking the details to make sure it's the right film/database entry


- query database for films by entering your search in the search field (below 'Suche')
    - you can choose which attributes are queried by selecting/not selecting the equivalent checkbuttons

## project modules and classes


### private_db.db_gui

#### class DB_GUI

- enter query in search bar
- select categories to be queried in with checkbuttons

-> query result is displayed in listbox
- select entry in listbox to view details

#### class WindowEditFilm

- insert film attributes to add/edit film 
- open filedialog to get cover path


- add:
    - you can get most of the film attributes from OMDB after entering the title 
- edit/remove:
    - open WindowLoadFilm to choose a film and load the attributes of the chosen film
    
#### class WindowLoadFilm

choose one film to edit/remove

### private_db.films.FilmeDB

#### class Film
attributes:
- title
- release year
- director
- FSK (German age approval)
- genre
- actors
- length
- cover path (path to a cover image)
- comment
- rating
- disc type (0=unknown, 1=BluRay, 2=DVD)

#### class FilmeDB

sqllite3 database to store films

functions to:
- add films
- edit films
- remove films


- query for films by attributes

### private_db.films.FilmImport

#### class OmdbFilmImport

get JSON data of films from 'Open Movie DataBase'

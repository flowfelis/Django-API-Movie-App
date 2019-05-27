# Django Movie API Project 
##How To Run It Locally
- Clone this repo
- Create a virtual environment
- Install dependencies `pip install -r requirements.txt`
- Run django dev server `./manage.py runserver` 
- API is served at localhost:8000
###General Info
- For POST /comments and GET /comments, **imdbID** should be passed, instead of application database primary key id.
Because imdbID's are guaranteed to be unique.
- The public app is hosted at Digital Ocean with HTTPS enabled. [Click here](movieapi.flowfelis.com) to try it.
- Tests are at movieapi/tests.py, and test data is available at movieapi/fixtures/test_data.json. `manage.py loaddata` can be used.

##Details
####POST /movies

- Request body should contain only movie title, and named as `movie_title`. for example-> `movie_title=braveheart`
- Its presence is validated with the external API
- Duplicate movie saving is not allowed, by checking records with the same imdb ID in the database.
- All movie data from external API are saved to application database, except Year, Ratings and Response,
because there is another data related
- Newly saved movie data is returned

####GET /movies
- If no parameter is given, it will return all movies in the application database
- `order_by=title`, or `order_by=rating` can be used to order by movie title, or imdb rating
- `desc=true` parameter can be given to reverse the order
- if `desc` parameter is given without the `order_by` parameter, then will return all movies without ordering

####POST /comments
- Request body should contain imdbID of movie already present in database, and comment text body.
for example ->`movie_id=tt0112573` and `comment=simple comment`
- Comment is saved to application database and returned in request response.

####GET /comments
- Fetches list of all comments present in application database
- By passing associated movie imdbID, allows filtering comments. for example -> `movie_id=tt0112573` 

####GET /top
- Returns top movies already present in the database ranking based on a number of comments added to the movie
 in the specified date range. The response includes the ID of the movie(*in this case, the application database id*), position in rank and total number of comments (in the specified date range). 
 - Date range is specified like this example --> `start_date=2019-5-21` and `end_date=2019-5-26`. Month can be 0 padded(ie. *05*).
 Date seperator must be hyphen(`-`).

Thank you! 

Alican
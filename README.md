# Django Movie API Project 

## General Info

- The public app is hosted at Digital Ocean, HTTPS enabled, with Docker, Docker-Compose, Gunicorn and NGINX. [Click here](https://movieapi.flowfelis.com/movies) to try it.
Always use `https`, when using the public app. Post requests might not work, when used with `http`.
- For POST /comments and GET /comments, **imdbID** should be passed, instead of application database primary key id
Because imdbID's are guaranteed to be unique
- Tests are at movieapi/tests.py, and test data is available at movieapi/fixtures/test_data.json. `manage.py loaddata` can be used
##### Which Third Party Libraries Are Used?
- Django Rest Framework for easy API Creation
- requests library to make a call to external movie API

### How To Run It Locally
- Make sure `docker` and `docker-compose` are installed, and `docker service` is running on your system
- Clone this repo
- Run `docker-compose up`, under the cloned repo's directory
- Go to `localhost:8000/movies` from your favourite browser and play around with API
- Database will be persisted in `postgres_data` folder, in case you restart docker services
- When you are done playing around, run `docker-compose down`

## Details
#### POST /movies

- Request body should contain only movie title, and named as `movie_title`. for example-> `movie_title=braveheart`
- Its presence is validated with the external API
- Duplicate movie saving is not allowed, by checking records with the same imdb ID in the database
- All movie data from external API are saved to application database, except Year, Ratings and Response,
because there is another data related
- Newly saved movie data is returned

#### GET /movies
- If no parameter is given, it will return all movies in the application database
- `order_by=title`, or `order_by=rating` can be used to order by movie title, or imdb rating
- `desc=true` parameter can be given to reverse the order
- if `desc` parameter is given without the `order_by` parameter, then will return all movies without ordering

#### POST /comments
- Request body should contain imdbID of movie already present in database, and comment text body
for example ->`movie_id=tt0112573` and `comment=simple comment`
- Comment is saved to application database and returned in request response

#### GET /comments
- Fetches list of all comments present in application database
- By passing associated movie imdbID, allows filtering comments. for example -> `movie_id=tt0112573` 

#### GET /top
- Returns top movies already present in the database ranking based on a number of comments added to the movie
 in the specified date range. The response includes the ID of the movie(*in this case, the application database id*), position in rank and total number of comments (in the specified date range)
 - Date range is specified like this example --> `start_date=2019-5-21` and `end_date=2019-5-26`. Month can be 0 padded(ie. *05*)
 Date seperator must be hyphen(`-`)

Thank you! 

Alican
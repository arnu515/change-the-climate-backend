# ChangeTheClimate (BACKEND)
[Change the Climate](https://changetheclimate.gq) is a website where you can tell others what you've done for the betterment of the environment and to combat climate change.

### Quickstart

0. Have a Redis and Postgres database ready

1. Clone the repository

```
git clone https://github.com/arnu515/change-the-climate-backend.git backend
cd backend
```

2. Set environment variables, either in .env or in your terminal with the `export` command

> Replace the values in angle brackets (`<>`)

```
SQLALCHEMY_DATABASE_URI=<URL_OF_POSTGRES_DATABASE>
REDIS_URI=<URL_OF_REDIS_DATABASE>
SECRET=<any strong secret>
JWT_EXPIRES_IN=<number of seconds after which a user is logged out. Eg: 86400 for 1 day>
```

3. Run the server

Using docker:
```
docker run -dp 80:80 "$(docker build -q .)"
```

Locally:
```bash
# You need pipenv for this
# pip install pipenv

pipenv --python 3.8
pipenv install
export FLASK_APP=main:app
pipenv run flask db migrate # Creates tables and relations in the database
pipenv run flask run
```

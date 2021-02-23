FROM python:3.8

ENV FLASK_APP main:app

ENV FLASK_ENV production

RUN mkdir /app

WORKDIR /app

COPY Pipfile* ./

RUN pip install pipenv

RUN pipenv --python 3.8

RUN pipenv install

COPY . .

RUN pipenv run flask db upgrade

EXPOSE 80

ENTRYPOINT ["sh", "start.sh"]
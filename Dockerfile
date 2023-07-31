FROM python:3.10.11
RUN pip install pipenv
WORKDIR /bot
COPY Pipfile /bot/
COPY Pipfile.lock /bot/
RUN pipenv --python 3.10.11
RUN pipenv install --deploy --ignore-pipfile
COPY . /bot
CMD pipenv run python bot.py
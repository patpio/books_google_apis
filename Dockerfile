FROM python:3.10

ENV APP_CODE=/code
RUN mkdir $APP_CODE
WORKDIR $APP_CODE

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY Pipfile Pipfile.lock $APP_CODE/
RUN pip install pipenv && pipenv install --system

COPY . $APP_CODE/

CMD python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8000
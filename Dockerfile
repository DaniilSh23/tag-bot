FROM python:3.10-slim

RUN mkdir "tag_bot"

COPY requirements.txt /tag_bot/

RUN apt update

RUN apt install python3-dev libpq-dev postgresql-contrib curl -y

RUN apt-get install build-essential -y

RUN pip install psycopg2-binary

RUN python -m pip install --no-cache-dir -r /tag_bot/requirements.txt

COPY . /tag_bot/

WORKDIR /tag_bot

# Ниже команды для создания суперпользователя в Django
ENV DJANGO_SUPERUSER_USERNAME=admin
ENV DJANGO_SUPERUSER_PASSWORD=admin
ENV DJANGO_SUPERUSER_EMAIL=my@dmin.com

# Открываем 8000 порт
EXPOSE 8000

# Запуск
ENTRYPOINT ["/tag_bot/entrypoint.sh"]
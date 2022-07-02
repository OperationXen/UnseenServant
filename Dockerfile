FROM ubuntu:20.04

WORKDIR /unseen_servant
COPY . /unseen_servant

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV TZ=Europe/London

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install python external libs, and web server packages
RUN apt update && apt install git python3 python3-pip python3-venv apache2 libapache2-mod-wsgi-py3 libpq-dev -y

# Create python virtual env
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Update tooling and install required packages
RUN pip install --upgrade pip setuptools wheel && pip install -r requirements.txt
RUN python manage.py collectstatic --no-input
# Enable site
RUN mv /unseen_servant/deploy/bot.conf /etc/apache2/sites-available/000-default.conf && a2ensite 000-default

CMD ["apachectl", "-D",  "FOREGROUND"]

FROM ghcr.io/astral-sh/uv:trixie-slim

WORKDIR /unseen_servant
COPY . /unseen_servant

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TZ=Europe/London

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install python external libs, and web server packages
RUN apt update && apt install apache2 libapache2-mod-wsgi-py3 libpq-dev -y

# Update tooling and install required packages
RUN uv sync --no-dev
RUN touch debugging.log && chmod 777 debugging.log
RUN uv run manage.py collectstatic --no-input
# Enable site
RUN mv /unseen_servant/deploy/bot.conf /etc/apache2/sites-available/000-default.conf && a2ensite 000-default

CMD ["apachectl", "-D",  "FOREGROUND"]

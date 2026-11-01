FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim

WORKDIR /unseen_servant
COPY . /unseen_servant

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TZ=Europe/London

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Update tooling and install required packages
RUN uv sync --no-dev
RUN touch debugging.log && chmod 777 debugging.log

CMD ["uv", "run", "manage.py", "startbot"]

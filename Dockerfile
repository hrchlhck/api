FROM python:3.12-slim

RUN pip install uv

COPY --exclude=.venv . /app

WORKDIR /app

RUN uv sync --locked

CMD ["uv", "run", "-m", "fastapi", "run"]
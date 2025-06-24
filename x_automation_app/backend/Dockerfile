FROM python:3.12-slim

WORKDIR /code

RUN pip install uv

COPY pyproject.toml uv.lock ./

RUN uv pip install --system .

COPY ./app ./app
COPY ./.env ./.env

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 
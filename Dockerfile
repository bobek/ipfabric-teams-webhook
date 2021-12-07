# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY src/* .

CMD [ "python3", "-m" , "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
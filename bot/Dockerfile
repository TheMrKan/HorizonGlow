FROM python:3.12

WORKDIR /usr/src/app/bot

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COMMAND ["python3", "-m", "main.py"]
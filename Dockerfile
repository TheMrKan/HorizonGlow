FROM python:3.12

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g' /usr/src/app/entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh

COPY . .

RUN mkdir -p product_files

# setup cron https://stackoverflow.com/a/37458519
RUN apt-get update && apt-get -y install cron
ADD prune_files.crontab /etc/prune_files.crontab
RUN crontab /etc/prune_files.crontab

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
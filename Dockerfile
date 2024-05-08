FROM python:3

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt
RUN playwright install
RUN playwright install-deps

CMD [ "python", "./bot.py" ]
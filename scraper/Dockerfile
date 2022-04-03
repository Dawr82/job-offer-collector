FROM python:3.8.3

WORKDIR ./app

COPY ./requirements.txt ./requirements.txt

RUN pip3 install -r ./requirements.txt

RUN mkdir log

COPY . .

CMD ["python3", "main.py", "extract", "mongo"]

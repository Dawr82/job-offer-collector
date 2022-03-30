FROM ubuntu:latest

RUN apt-get -y update && apt-get -y install python3-pip

COPY ./requirements.txt ./app/requirements.txt

WORKDIR ./app

RUN pip3 install -r ./requirements.txt

COPY . .

EXPOSE 5000

ENTRYPOINT ["python3"]

CMD ["app.py"]
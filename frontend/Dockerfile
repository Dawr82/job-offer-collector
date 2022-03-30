FROM python:3.9-alpine3.14

WORKDIR ./app

COPY ./requirements.txt ./requirements.txt

RUN pip3 install -r ./requirements.txt

COPY . .

EXPOSE 9000

ENTRYPOINT ["streamlit", "run"]

CMD ["charts.py", "--server.port", "9000"]
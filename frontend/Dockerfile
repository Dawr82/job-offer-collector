FROM python:3.8.3

WORKDIR ./app

COPY ./requirements.txt ./requirements.txt

RUN pip3 install -r ./requirements.txt

COPY . .

EXPOSE 8501

ENTRYPOINT ["streamlit", "run"]

CMD ["charts.py", "--server.port", "8501"]

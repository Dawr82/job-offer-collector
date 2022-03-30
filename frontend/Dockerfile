FROM python:3.8.3

WORKDIR ./app

RUN pip3 install streamlit && pip3 install pandas

COPY . .

EXPOSE 9000

ENTRYPOINT ["streamlit", "run"]

CMD ["charts.py", "--server.port", "9000"]

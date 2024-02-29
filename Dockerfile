FROM python:3

RUN pip install python-dotenv

COPY . /app

WORKDIR /app/scripts

RUN pip install -r ./requirements.txt

CMD ["python", "./graphql.py"]

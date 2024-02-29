FROM python:3.9.18

COPY . ./app

WORKDIR /app

RUN pip install python-dotenv

RUN pip install -r ./scripts/requirements.txt

CMD ["python", "./scripts/graphql.py"]

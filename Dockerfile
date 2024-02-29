FROM python:3.9.18

WORKDIR /app

RUN pip install python-dotenv

COPY . .

RUN pip install -r ./scripts/requirements.txt

CMD ["python", "./scripts/graphql.py"]

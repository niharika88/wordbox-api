FROM python:3.6-slim-buster

ENV NUM_OF_PARAGRAPHS 1
ENV NUM_OF_SENTENCES_IN_PARAGRAPH 50

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 80

CMD ["flask", "run", "--host=0.0.0.0", "--port=80"]
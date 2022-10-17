import os
from re import U
import psycopg2
from count_helper import WordCountWithDefinitions, get_word_definition
from dotenv import load_dotenv
from flask import Flask, request
from query import postgres_queries
import requests
# import threading

load_dotenv()  # loads env vars from .env file

# Get variables from env config
postgres_url = os.environ.get("DATABASE_URL")
num_para = os.environ.get("NUM_OF_PARAGRAPHS")
num_sentences = os.environ.get("NUM_OF_SENTENCES_IN_PARAGRAPH")

flask_app = Flask(__name__)

# Define global variables
connection = psycopg2.connect(postgres_url)

# Setup database table (ideally we do this with migrations)
with connection:
    with connection.cursor() as cursor:
        cursor.execute(postgres_queries.CREATE_TABLE_PARAGRAPHS)
        # cursor.execute(postgres_queries.CREATE_TABLE_DICTIONARY)


# Populate frequency word map from existing paragraphs in the database
word_counter = WordCountWithDefinitions()
word_counter.populate_word_counter_map(connection)

@flask_app.route("/")
def hello():
    return "Welcome to wordbox!"


@flask_app.route("/healthcheck")
def healthcheck():
    return "I'm fine, what about you?"


@flask_app.route("/get")
def get_paragraph():
    # Get a new paragraph
    url = "http://metaphorpsum.com/paragraphs/{}/{}".format(num_para, num_sentences)
    response = requests.get(url)
    if response:
        para = response.text
        word_counter.update_most_frequent_wordmap(para)

        with connection:
            with connection.cursor() as cursor:
                cursor.execute(postgres_queries.INSERT_DATA, [para])
        return {"message": "Fetched and inserted a new paragraph.", "paragraph": para}, 201
    else:
        return {"Error": response.text}, response.status_code


@flask_app.route("/search")
def search_for_words_in_paragraphs():
    op=request.args.get('operator', "and")
    words=request.args.get('words', "")
    # Split words and remove empty whitespaces
    words = [w.strip() for w in words.split(",") if w.strip()]

    if not words or op not in ["or", "and"]:
        return {"Error": "Please input some words and a valid operator(or/and), default operator will be 'and'"}, 400

    # create regex for query based on operator type
    regex = ""
    response = []
    if op == "and":
        regex = "".join(["(?=.*{})".format(w) for w in words])
    if op == "or":
        regex = "|".join(words)
    
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(postgres_queries.SEARCH_FOR_PARAGRAPHS, [regex])
            data = cursor.fetchall()

            for para in data:
                response.append(para[0])

    return {"Operator": op, "Words": words, "Matching Paragraphs": response}


@flask_app.route("/dictionary")
def get_most_freq_words_definition():

    most_freq_words = word_counter.get_most_frequent_words(10)

    if len(most_freq_words) == 0:
        return {"Error": "No words in freq map."}, 500

    response = {}
    for word, _ in most_freq_words:
        response[word] = get_word_definition(word)

    return response, 200

# Uncomment if we want to run the app with python app.py
# if __name__ == '__main__':
#     app.run()
from collections import Counter
import re
from typing import Any
from query import postgres_queries
import requests


class WordCountWithDefinitions(object):
    # add dynamic dictionary
    word_definition_map = {}

    def __init__(self) -> None:
        # word frquency counter map
        self.word_counter_map = Counter()

    def update_most_frequent_wordmap(self, para: str):
        new_count = _get_word_count(para)
        self.word_counter_map.update(new_count)

    def populate_word_counter_map(self, connection: Any):
        print("0", connection)
        with connection:
            print("1", connection)
            with connection.cursor() as cursor:
                print("2", connection)
                print("3", cursor)
                cursor.execute(postgres_queries.GET_ALL_PARAGRAPHS)
                data = cursor.fetchall()
                print("Generating a word frequency map for {} paragraphs".format(len(data)))
                for para in data:
                    self.update_most_frequent_wordmap(para[0])

    def get_most_frequent_words(self, count: int) -> list:
        return self.word_counter_map.most_common(count)


def _get_word_count(para: str):
    # Force to all be lowercase for better frequency count.
    para = para.lower()

    # Remove everything except words and space
    para = re.sub("[^\\w ]", "", para)
    # print("Sanitized sentence: ", para)

    return Counter(para.strip().split(" "))


def get_word_definition(word: str) -> str:
    if word in WordCountWithDefinitions.word_definition_map:
        return WordCountWithDefinitions.word_definition_map[word]
    else:
        # get definition from external API
        # print("Fetching definition of '{}' from third party API".format(word))
        response = requests.get("https://api.dictionaryapi.dev/api/v2/entries/en/{}".format(word))
        if response:
            data = response.json()[0]
            if "word" in data:
                # get the first definition from the response.
                definition = data.get("meanings")[0].get("definitions")[0].get("definition")
                print("Got new def for {}: {}".format(word, definition))
                WordCountWithDefinitions.word_definition_map[word] = definition
                return definition
            else:
                print("No definitions returned for word: {}".format(word))
                return "No definitions returned"
        else:
            return response.json()["message"]

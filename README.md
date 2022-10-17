# Introduction

Create an API with the following 3 endpoints:
* get/
    * Fetch a paragraph and store it
    * No params are needed.
    * When this endpoint is hit, it should fetch 1 paragraph from http://metaphorpsum.com/ with 50 sentences and store it in a persistent storage layer and return it.
* search/
    * search through stored paragraphs
    * allow providing multiple words and one of the two operators: 'or' or 'and'
        * “one”, “two”, “three”, with the “or” operator should return any paragraphs that have at least one the words “one”, “two” or “three”
        * “one”, “two”, “three”, with the “or” operator should return paragraphs that have all the words “one”, “two” or “three”
* dictionary/
    * Should return the definition of the top 10 words (frequency) found in the all the
paragraphs currently store in the system.
    * Word definition should retrieved from https://dictionaryapi.dev/

# Setup Instructions
* Without Docker:
    * Install python3
    * Install postgresql ([homebrew](https://wiki.postgresql.org/wiki/Homebrew))
    * Run postgres server
    * Download project wordbox-api
    * Activate env with (if running without Docker)
        * `source .venv/bin/activate`
        * `pip install -r requirements.txt`  
    * Run application (outside Docker)
        * `flask run`
* To run a docker container, under project root directory:
    * `docker compose up --build`
* Open the browser, goto following urls (for a run without Docker, use `http://127.0.0.1:5000/`):
    * `http://localhost/` - Welcome page
    * `http://localhost/healthcheck` - healthcheck
    * `http://localhost/get` - fetches a paragraph
    * `http://localhost/get` - fetches another paragraph
    * `http://localhost/dictionary` - fetches 10 most frequently occuring words and their definitions (will be slow the first time but faster afterwards)
    * `http://localhost/search?operator=or&words=random,morerandom,mostrandom` - searches for given words in paragraphs stored in postgres (no results since words are random)
    * `http://localhost/search?operator=or&words=random,morerandom,mostrandom` - fails since incorrect operator
    * `http://localhost/search?operator=notoperator&words=random,morerandom,mostrandom` - fails since missing words input
    * `http://localhost/search?operator=or&words= ` - fails since missing words input
    * `http://localhost/search?operator=or&words=granddaughter,himalayan` - successfull search with paragraphs returned (enter some words that are likely to occur in fetched paragraphs)

# Testing

* Goto project home directory
* Run
    * `source .venv/bin/activate`
* Run tests
    * `pytest`

# Simple Design

* App.py - houses the flask app initialization and routing and controller logic
    * IF the application grows, would definitely refactor out routing logic/models/db access and business logic
* count_helper.py - houses all the helper/util methods to maintain a count of most frequent words and their corresponding definitions
* When the app starts, we populate a map (maintained in memory) with word frequency from all paras present in DB. This is done so that later we do we spend too much time on dictionary call.
* On every **get** call, we fetch a new paragraph, store it in DB and return it to the user
    * Another imp step here is to up the memory map (mentioned above) with the word count frequency of the new paragraph, so that the map is up to date
* On search call, it's a basic regex match search on paras stored in DB. Have some basic query param validations as well.
* On dictionary call, the helper methods come into picture and drastically reduce it's execution time (calling third party).
    * On the first time call, we already have the MAP containing most frequent words in memory, we just get top 10 from that map
    * For the definitions, for the first time, we don't have it, so we do a API call to get their definitions
    * But before returning response to the user, we also store it in another map (word -> definition) (**Caching**)
    * On every subsequent calls, we always have the top 10 most frequent words in first map and their definitions in second map, so it's always faster
    * On every **get** call, we are anyways updating the first map, so list is up to date and if we encounter a new word in top 10 whose definition is not yet present in second map, we just fetch that one and the call to dictionary is still fast.

# Assumptions

* Didn't create db migrations or ORM models as it's a small app with very simple schema
* Did not store created_at/updated_at fields in db as not required in current scenario
* Data size is small, so limited performance impact on search/dictionary apis
    * To improve /dictionary call perf, we precompute and store more frequent words in memory (for large data, can use a persistent cache like Redis to avoid warming it up on every restart)
* No persistence for word_counter right now, but could be done before productionzing (Redis e.g. in earlier point)
* Assuming limited/very less traffic, didn't bother about race conditions in global map access
* Have implemented a simple word search but we can improve perf with trigram search or postgres text search 


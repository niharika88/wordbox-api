import pytest
from app import flask_app
from unittest import mock


@pytest.fixture
def mock_request():
    with mock.patch(
        "app.requests",
        autospec=True,
    ) as _mock:
        yield _mock


@pytest.fixture
def mock_get_word_definition():
    with mock.patch(
        "app.get_word_definition",
        autospec=True,
    ) as _mock:
        yield _mock


@pytest.fixture
def mock_word_counter():
    with mock.patch(
        "app.WordCountWithDefinitions.get_most_frequent_words",
        autospec=True,
    ) as _mock:
        yield _mock


@pytest.fixture(scope="module")
def test_client():
    """Configures the app for testing
    """

    with flask_app.test_client() as client:
        with flask_app.app_context():
            yield client


def test_hello(test_client):
    response = test_client.get("/")
    assert response.status_code == 200
    assert response.text == "Welcome to wordbox!"


def test_healthcheck(test_client):
    response = test_client.get("/healthcheck")
    assert response.status_code == 200
    assert response.text == "I'm fine, what about you?"


def test_get_paragraph(test_client, mock_request):

    # mock the response
    mock_response = mock.MagicMock()
    mock_response.status_code = 200
    mock_response.text = "one.two.three.four.five"
    mock_request.get.return_value = mock_response


    response = test_client.get("/get")
    assert response.status_code == 201
    assert response.json["paragraph"] == "one.two.three.four.five"


def test_search_for_words_in_paragraphs(test_client):

    # Invalid input - wrong operator
    response = test_client.get("/search?operator=INVALID&words=one,two")
    assert response.status_code == 400
    assert "Error" in response.json 

    # Invalid input - no words to search
    response = test_client.get("/search?operator=or&words=")
    assert response.status_code == 400
    assert "Error" in response.json 

    # Valid input
    response = test_client.get("/search?operator=or&words=one,two")
    assert response.status_code == 200
    assert len(response.json["Matching Paragraphs"]) != 0


def test_get_most_freq_words_definition(test_client, mock_word_counter, mock_get_word_definition):

    # Freq words list is empty, error response.
    mock_word_counter.return_value = []

    response = test_client.get("/dictionary")

    assert response.status_code == 500
    assert "Error" in response.json


    # Freq words list is NOT empty.
    mock_word_counter.return_value = [("one", 3),("two", 2),("three", 1)]
    mock_get_word_definition.return_value = "def" # mock definition as "def" for each word

    response = test_client.get("/dictionary")

    assert response.status_code == 200

    assert response.json == {'one': 'def', 'three': 'def', 'two': 'def'}

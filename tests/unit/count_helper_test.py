import pytest
from unittest import mock
from collections import Counter
from count_helper import _get_word_count, WordCountWithDefinitions, get_word_definition


@pytest.fixture
def mock_connect():
    with mock.patch(
        "psycopg2.connect",
        autospec=True,
    ) as _mock:
        yield _mock


def test_update_most_frequent_wordmap():
    c = WordCountWithDefinitions()
    c.word_counter_map = Counter(["this", "para"])

    c.update_most_frequent_wordmap("This is the para. Is this a para?")

    assert c.word_counter_map == Counter({
        "this": 3,
        "is": 2,
        "the": 1,
        "para": 3,
        "a": 1,
    })


def test_get_most_frequent_words():
    c = WordCountWithDefinitions()
    c.word_counter_map = Counter({"this": 45, "a": 32,  "para":3})

    response = c.get_most_frequent_words(2)

    assert response == [("this", 45), ("a", 32)]


def test_get_word_count():
    input_text = """
This is the para. Is this a para?
    """
    response = _get_word_count(input_text)

    assert response == Counter(["this", "this", "is", "is", "a", "the", "para", "para"])


@mock.patch("count_helper.requests", autospec=True)
def test_get_word_definition(mock_request):
    WordCountWithDefinitions.word_definition_map = {"a": "DEFINE#1", "b": "DEFINE#2"}
    
    # definition already cached.
    w_def = get_word_definition("a")
    assert w_def == "DEFINE#1"
    mock_request.get.assert_not_called()

    # definition fetched from third party.
    
    # mock the response
    mock_response = mock.MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{
        "word": "c",
        "meanings":[{
            "definitions":[{
                "definition": "DEFINE#3"
            }]
        }]
    }]
    mock_request.get.return_value = mock_response

    w_def = get_word_definition("c")
    assert w_def == "DEFINE#3"
    mock_request.get.assert_called_once()

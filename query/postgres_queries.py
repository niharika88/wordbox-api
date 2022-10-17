# Create the table to store paragraphs.
CREATE_TABLE_PARAGRAPHS = (
    """CREATE TABLE IF NOT EXISTS paragraphs (id SERIAL PRIMARY KEY, data TEXT);"""
)

# [For future] Create the table to store word definitions fetched from third party.
CREATE_TABLE_DICTIONARY = (
    """CREATE TABLE IF NOT EXISTS dictionary (id SERIAL PRIMARY KEY, word TEXT, definition TEXT);"""
)

# Insert paragraphs.
INSERT_DATA = (
    """INSERT INTO paragraphs (data) VALUES (%s);"""
)

# Get all paragraphs (for creating a word frequency mapping at server initialization).
GET_ALL_PARAGRAPHS = (
    """SELECT data FROM paragraphs;"""
)

# Get all paragraphs matching a certain regular expression.
SEARCH_FOR_PARAGRAPHS = (
    """SELECT data FROM paragraphs WHERE data ~* %s;"""
)

# [For future] Get definition of given words from dictionary table.
SEARCH_DEFINITIONS = (
    """SELECT word, definition FROM dictionary WHERE word IN (%s)"""
)
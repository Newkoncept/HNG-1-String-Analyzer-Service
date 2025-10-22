from http import HTTPStatus
import hashlib
import re


def status_error_code_displayer(statusValue):
    return f"{statusValue} {HTTPStatus(statusValue).phrase}"


def get_sha256_hash(text: str) -> str:
    # encode the string to bytes, because hashlib works on bytes
    encoded_text = text.encode('utf-8')
    
    # create a sha256 hash object
    sha256_hash = hashlib.sha256(encoded_text)
    
    # return the hexadecimal digest (human-readable string)
    return sha256_hash.hexdigest()


def is_palindrome(value):
    reversed_value = value[::-1]
    return reversed_value == value

def unique_character(value):
    unique_values = set(value)
    return len(unique_values)

def word_count(value):
    return len(value.split())

def character_map(value):
    frequency_map = {}

    for element in value:
        if element in frequency_map:
            frequency_map[element] += 1
        else:
            frequency_map[element] = 1

    return frequency_map

def nlf(text):
    filters = {}
    

    # --- palindromic / non-palindromic ---
    if re.search(r"\b(?:non[-\s]?|not\s+)palindrom(?:ic|e|es)?\b", text, re.IGNORECASE):
        filters["is_palindrome"] = False
    elif re.search(r"\bpalindrom(?:ic|e|es)?\b", text, re.IGNORECASE):
        filters["is_palindrome"] = True


    
    # --- word count (focus on single word; extend as needed) ---
    match = re.search(r"\b(?:(single|one)|(\d+)|two|three)\s+words?\b", text, re.IGNORECASE)

    if match:
        word = match.group(1)
        digit = match.group(2)

        if word in ("single", "one"):
            filters["word_count"] = 1
        elif digit == "2" or re.search(r"\btwo\b", text, re.IGNORECASE):
            filters["word_count"] = 2
        elif digit == "3" or re.search(r"\bthree\b", text, re.IGNORECASE):
            filters["word_count"] = 3


    # --- contains specific letter ---
    # Supports:
    #   "letter z", "character z", "char z"
    #   "containing z", "contain the letter z"
    #   "with the letter 'A'", "has letter b"
    #   Handles quotes and any alphabetic letter (A–Z, a–z)
    m = re.search(r"""(?ix)
        \b(?:letter|char(?:acter)?)\s*['"]?([A-Z])['"]?\b
    |   \bcontain(?:ing)?\s+(?:the\s+letter\s+)?['"]?([A-Z])['"]?\b
    |   \bwith\s+(?:the\s+letter\s+)?['"]?([A-Z])['"]?\b
    |   \bhas\s+(?:the\s+letter\s+)?['"]?([A-Z])['"]?\b
    """, text)
    if m:
        # Pick whichever group matched, normalize to lowercase
        ch = next(g for g in m.groups() if g)
        filters["contains_character"] = ch.lower()



    # --- "first vowel" heuristic → a ---
    if re.search(r"\bfirst\s+vowel\b", text, re.IGNORECASE):
        filters["contains_character"] = "a"



    # --- length phrases ---
    # Handles:
    #   "longer than 10 characters", "over 10 characters"
    #   "at least 10 characters"
    #   "shorter than 10 characters", "under 10 characters"
    #   "at most 10 characters"
    # --- length phrases ---
    # "longer than 10 characters" → min_length = 11
    m = re.search(r"\b(longer\s+than|more\s+than|over)\s+(\d+)\s+characters?\b", text)
    if m:
        filters["min_length"] = int(m.group(2)) + 1

    # "at least 10 characters" → min_length = 10
    m = re.search(r"\bat\s+least\s+(\d+)\s+characters?\b", text)
    if m:
        filters["min_length"] = int(m.group(1))

    # "shorter than 10 characters" → max_length = 9
    m = re.search(r"\b(shorter\s+than|less\s+than|under)\s+(\d+)\s+characters?\b", text)
    if m:
        filters["max_length"] = int(m.group(2)) - 1

    # "at most 10 characters" → max_length = 10
    m = re.search(r"\bat\s+most\s+(\d+)\s+characters?\b", text)
    if m:
        filters["max_length"] = int(m.group(1))



    return filters


def query_set_logic(self, query):
    print(self.filters)
    if 'is_palindrome' in self.filters:
        query = query.filter(properties__is_palindrome=self.filters['is_palindrome'])

    if 'word_count' in self.filters:
        query = query.filter(properties__word_count__exact=self.filters['word_count'])

    if 'min_length' in self.filters:
        query = query.filter(properties__length__gte=self.filters['min_length'])

    if 'max_length' in self.filters:
        query = query.filter(properties__length__lte=self.filters['max_length'])

    if 'contains_character' in self.filters:
        query = query.filter(value__icontains=self.filters['contains_character'])

    return query

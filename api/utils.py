from http import HTTPStatus
import hashlib


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
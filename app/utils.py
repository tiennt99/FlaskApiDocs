import base64
import hashlib
import random
import re
import string
import datetime
from pytz import timezone
from app.extensions import parser
from marshmallow import fields, validate as validate_

# Regex validate
RE_ONLY_NUMBERS = r'^(\d+)$'
RE_ONLY_CHARACTERS = r'^[a-zA-Z]+$'
RE_ONLY_NUMBER_AND_DASH = r'^[-\d]+$'
RE_ONLY_LETTERS_NUMBERS_PLUS = r'^[+A-Za-z0-9]+$'
REGEX_EMAIL = r'/(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{6,}/'
REGEX_PHONE_NUMBER = r'^\+?[0-9]{0,20}$'
REGEX_OTP = r'[0-9]{6}'
REGEX_FULLNAME_VIETNAMESE = r"([^0-9`~!@#$%^&*(),.?'\":;{}+=|<>_\-\\\/\[\]]+)$"

REGEX_ADDRESS_VIETNAMESE = r"([^`~!@#$%^&*().?'\":;{}+=|<>_\-\\\[\]]+)$"
REGEX_VALID_PASSWORD = r'^(?=.*[0-9])(?=.*[a-zA-Z])(?!.* ).{8,16}$'


def are_equal(arr1: list, arr2: list) -> bool:
    """
    Check two array are equal or not
    :param arr1: [int]
    :param arr2: [int]
    :return:
    """
    if len(arr1) != len(arr2):
        return False

    # Sort both arrays
    arr1.sort()
    arr2.sort()

    # Linearly compare elements
    for i, j in zip(arr1, arr2):
        if i != j:
            return False

    # If all elements were same.
    return True


def get_timestamp_now() -> int:
    """
        Returns:
            current time in timestamp
    """
    time_zon_sg = timezone('Asia/Ho_Chi_Minh')
    return int(datetime.datetime.now(time_zon_sg).timestamp())


def password_encode(password):
    """
    :param password:
    :return:
    """
    hash_password = hashlib.md5(password.encode())
    return hash_password.hexdigest()


def check_format_email(email):
    """
    :param email:
    :return:
    False if email format  incorrect else true
    """
    # pass the regular expression
    # and the string in search() method
    regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    return re.search(regex, email)


def check_format_password(password):
    """
    :param password:
    :return:
    False if password format  incorrect else true
    """
    # pass the regular expression
    # and the string in search() method
    regex = r'/(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{6,}/'
    return re.search(regex, password)


def escape_wildcard(search):
    """
    :param search:
    :return:
    """
    search1 = str.replace(search, '\\', r'\\')
    search2 = str.replace(search1, r'%', r'\%')
    search3 = str.replace(search2, r'_', r'\_')
    search4 = str.replace(search3, r'[', r'\[')
    search5 = str.replace(search4, r'"', r'\"')
    search6 = str.replace(search5, r"'", r"\'")
    return search6

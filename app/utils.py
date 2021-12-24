import base64
import random
import re
import string
import datetime
from pytz import timezone
from app.extensions import parser
from marshmallow import fields, validate as validate_


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


def password_encoder(password):
    """
    :param password:
    :return:
    """
    alpha = 'abcdefghijklmnopqrstuvwxyz'
    password = password.encode('ascii')
    password1 = base64.b64encode(password)
    password2 = random.choice(alpha) + password1.decode('ascii') + random.choice(alpha)
    return password2


def password_decoder(password_hash):
    """
    :param password_hash:
    :return:
    """
    password = password_hash[1: len(password_hash) - 1]
    print(password)
    password1 = base64.b64decode(password)
    return password1.decode('ascii')


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


def get_random_alphanumeric_string(length):
    """
    :param length:
    :return:
    random password
    """
    symbol_list = ["@", "$", "!", "%", "*", "?", "&"]
    number = '0123456789'
    letters_and_digits = string.ascii_letters + string.digits
    result_str = ''.join((random.choice(letters_and_digits) for i in range(length)))
    return '{}{}{}'.format(result_str, random.choice(symbol_list), random.choice(number))


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


def parse_req(argmap):
    """
    Parser request from client
    :param argmap:
    :return:
    """
    return parser.parse(argmap)


class FieldString(fields.String):
    """
    validate string field, max length = 1024
    Args:
        des:

    Returns:

    """
    DEFAULT_MAX_LENGTH = 1024  # 1 kB

    def __init__(self, validate=None, requirement=None, **metadata):
        """

        Args:
            validate:
            metadata:
        """
        if validate is None:
            validate = validate_.Length(max=self.DEFAULT_MAX_LENGTH)
        if requirement is not None:
            validate = validate_.NoneOf(error='Dau vao khong hop le!', iterable={'full_name'})
        super(FieldString, self).__init__(validate=validate, required=requirement, **metadata)

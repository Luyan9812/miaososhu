import requests.exceptions
from requests.exceptions import RequestException


class StatusException(RequestException):

    def __init__(self, url: str, err_code: int):
        self.url = url
        self.err_code = err_code

    def __str__(self):
        return f'Fetch {self.url} errored with {self.err_code}'


def self_catch(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except StatusException as e:
            print(e)
        except requests.exceptions.RequestException as e:
            print(e.errno)
    return wrapper


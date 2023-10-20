#!/usr/bin/env python3
"""
web cache and tracker
"""
import requests
import redis
from functools import wraps

store = redis.Redis()


def count_url_access(method):
    """ Decorator counting how many times
    a URL is accessed """
    @wraps(method)
    def wrapper(url):
        cached_key = "cached:" + url
        cached_data = store.get(cached_key)
        if cached_data:
            return cached_data.decode("utf-8")

        count_key = "count:" + url
        try:
            res = method(url)
            html = res.text
            store.incr(count_key)
            store.set(cached_key, html)
            store.expire(cached_key, 10)
            return html
        except requests.exceptions.RequestException as e:
            # Handle the exception (e.g., log or re-raise) here
            raise e

    return wrapper


@count_url_access
def get_page(url: str) -> str:
    """ Returns HTML content of a url """
    res = requests.get(url)
    res.raise_for_status()  # Raise an exception for non-2xx responses
    return res

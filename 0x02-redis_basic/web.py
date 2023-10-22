#!/usr/bin/env python3

"""
Web cache and tracker
"""

import requests
import redis
from functools import wraps

store = redis.Redis()


def count_url_access(method):
    """Decorator counting how many times
    a URL is accessed and caching it for 10 seconds."""
    @wraps(method)
    def wrapper(url):
        cached_key = "cached:" + url
        cached_data = store.get(cached_key)
        if cached_data:
            return cached_data.decode("utf-8")

        count_key = "count:" + url
        html = method(url)

        store.incr(count_key)  # Increment the count
        store.set(cached_key, html, ex=10)  # Cache for 10 seconds
        return html

    return wrapper


@count_url_access
def get_page(url: str) -> str:
    """Returns HTML content of a URL."""
    res = requests.get(url)
    return res.text

# Example usage:
if __name__ == "__main__":
    url = "http://google.com"
    content = get_page(url)
    access_count = store.get("count:" + url).decode("utf-8")
    print(f"Content for {url}: {content}")
    print(f"Access count for {url}: {access_count}")

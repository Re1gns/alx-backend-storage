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
        html = method(url)

        store.incr(count_key)  # Increment the count
        store.set(cached_key, html)
        store.expire(cached_key, 10)
        return html

    return wrapper


@count_url_access
def get_page(url: str) -> str:
    """ Returns HTML content of a url """
    res = requests.get(url)
    return res.text


# Function to get the access count for a URL
def get_url_access_count(url: str) -> int:
    count_key = "count:" + url
    count = store.get(count_key)
    if count:
        return int(count)
    return 0

# Function to remove cached data for a URL
def remove_cached_data(url: str):
    cached_key = "cached:" + url
    store.delete(cached_key)

# Example usage:
url = "http://google.com"
content = get_page(url)
access_count = get_url_access_count(url)
print(f"Content for {url}: {content}")
print(f"Access count for {url}: {access_count}")
remove_cached_data(url)  # Remove cached data

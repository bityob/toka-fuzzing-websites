from aioresponses import aioresponses
from fastapi.testclient import TestClient
import pytest

from app.server import app
from app.utils import Url, urls_and_responses, USER_AGENT_HEADER


client = TestClient(app)
example_url = "https://www.example.com"
google_url = "https://google.com"


class ResponseMock:
    def __init__(self, text):
        self._text = text

    async def text(self):
        return self._text


@pytest.fixture(autouse=True)
def run_around_tests():
    urls_and_responses.clear()
    yield


# region safe_delete
def test_safe_delete_exists():
    from app.server import safe_delete
    u = Url(url="bla")
    urls_and_responses[u] = None
    assert safe_delete(u)
    assert len(urls_and_responses) == 0

def test_safe_delete_missing():
    from app.server import safe_delete
    u = Url(url="bla")
    assert not safe_delete(u)
    assert len(urls_and_responses) == 0
# endregion

# region run
async def test_run_one_url():
    u = Url(url=example_url)
    response_text = "Hello world!"

    with aioresponses() as m:
        m.get(example_url, body=response_text)

        response = client.post("/run", json=[u.dict()])

        assert response.status_code == 200
        assert response.text == f'"Run urls in background"'

        assert len(urls_and_responses) == 1

        background_response = urls_and_responses[u]
        assert await background_response.text() == response_text
        assert background_response.request_info.headers["User-Agent"]


async def test_run_one_url_with_user_agent():
    response_text = "Hello world!"
    user_agent = "fake-user-agent"
    u = Url(url=example_url, user_agent=user_agent)

    with aioresponses() as m:
        m.get(example_url, body=response_text)

        response = client.post("/run", json=[u.dict()])

        assert response.status_code == 200
        assert response.text == f'"Run urls in background"'

        assert len(urls_and_responses) == 1

        background_response = urls_and_responses[u]
        assert await background_response.text() == response_text
        assert background_response.request_info.headers["User-Agent"] == user_agent


async def test_run_multiple_urls():
    u1 = Url(url=example_url)
    u2 = Url(url=google_url)
    response_text = "Hello world!"

    with aioresponses() as m:
        m.get(example_url, body=response_text)
        m.get(google_url, body=response_text)

        response = client.post("/run", json=[u1.dict(), u2.dict()])

        assert response.status_code == 200
        assert response.text == f'"Run urls in background"'

        assert len(urls_and_responses) == 2

        background_response = urls_and_responses[u1]
        assert await background_response.text() == response_text
        assert background_response.request_info.headers["User-Agent"]

        background_response = urls_and_responses[u2]
        assert await background_response.text() == response_text
        assert background_response.request_info.headers["User-Agent"]


async def test_run_urls_and_clear_old_ones():
    def add_url():
        url_link = google_url
        u = Url(url=url_link)
        response = client.post("/add_url", json=u.dict())
        assert response.status_code == 200
        assert u in urls_and_responses
        return u

    add_url()
    response_text = "test"

    # No urls passed, so just clear all running urls
    with aioresponses() as m:
        m.get(example_url, body=response_text)
        example_url_object = Url(url=example_url)
        response = client.post("/run", json=[example_url_object.dict()])

        assert response.status_code == 200
        assert response.text == f'"Run urls in background"'

        assert len(urls_and_responses) == 1

        background_response = urls_and_responses[example_url_object]
        assert await background_response.text() == response_text
        assert background_response.request_info.headers["User-Agent"]

# endregion

# region run_once
async def test_run_once_without_user_agent():
    response_text = "fake"

    with aioresponses() as m:
        m.get(example_url, body=response_text)

        url_link = example_url
        u = Url(url=url_link)
        response = client.post("/run_once", json=u.dict())
        assert response.status_code == 200
        assert u in urls_and_responses
        assert response.text == f'"{response_text}"'
        assert urls_and_responses[u].request_info.headers["User-Agent"]

def test_run_once_with_user_agent():
    response_text = "fake2"
    user_agent_text = "fake-user-agent"

    with aioresponses() as m:
        m.get(example_url, body=response_text)

        url_link = example_url
        u = Url(url=url_link, user_agent=user_agent_text)
        response = client.post("/run_once", json=u.dict())
        assert response.status_code == 200
        assert u in urls_and_responses
        assert response.text == f'"{response_text}"'
        assert urls_and_responses[u].request_info.headers["User-Agent"] == user_agent_text
# endregion

# region add_url
def test_add_url():
    url_link = example_url
    url = dict(url=url_link)
    response = client.post("/add_url", json=url)
    assert response.status_code == 200
    assert Url(url=url_link) in urls_and_responses

def test_add_url_with_user_agent():
    url_link = example_url
    url = dict(url=url_link, user_agent="fake")
    response = client.post("/add_url", json=url)
    assert response.status_code == 200
    url_object = Url(url=url_link)
    # Check eq only by url
    assert url_object in urls_and_responses
    # Check user agent of the url key
    assert urls_and_responses.popitem()[0].user_agent == "fake"

def test_add_url_already_exists_and_get_updated():
    url_link = example_url
    url_object = Url(url=url_link, user_agent="old-user-agent")
    urls_and_responses[url_object] = None

    url = dict(url=url_link, user_agent="new-user-agent")
    response = client.post("/add_url", json=url)
    assert response.status_code == 200
    # Check eq only by url
    assert url_object in urls_and_responses
    # Check user agent of the url key
    assert urls_and_responses.popitem()[0].user_agent == "new-user-agent"
# endregion

# region remove_url
def test_remove_url():
    url_link = example_url
    url_object = Url(url=url_link, user_agent="old-user-agent")
    urls_and_responses[url_object] = None
    assert url_object in urls_and_responses

    response = client.post("/remove_url", json=url_object.dict())
    assert response.status_code == 200
    assert len(urls_and_responses) == 0

def test_remove_url_not_exists():
    url_link = example_url
    url_object = Url(url=url_link, user_agent="old-user-agent")
    assert url_object not in urls_and_responses

    response = client.post("/remove_url", json=url_object.dict())
    assert response.status_code == 404
    assert len(urls_and_responses) == 0
# endregion

# region get_last_response
def test_get_last_response_exists():
    text = "bla"
    u = Url(url=text)
    urls_and_responses[u] = ResponseMock(text=text)
    response = client.get("/get_last_response", json=u.dict())
    assert response.status_code == 200
    assert len(urls_and_responses) == 1
    # Weird bug in fast api test client, returns the string response with quotes marks 
    assert response.text == f'"{text}"'

def test_get_last_response_missing():
    text = "bla"
    u = Url(url=text)
    response = client.get("/get_last_response", json=u.dict())
    assert response.status_code == 404
    assert len(urls_and_responses) == 0
    # Weird bug in fast api test client, returns the string response with quotes marks 
    assert response.text == '"No such url"'
# endregion
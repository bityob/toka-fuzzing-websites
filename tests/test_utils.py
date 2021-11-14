import asyncio
from aiohttp.client import ClientSession

from app.utils import get_page, Url, urls_and_responses, run


async def test_get_page_without_user_agent():
    async with ClientSession() as s:
        u = Url(url="https://www.example.com")

        response = await get_page(s=s, url=u)

        assert urls_and_responses[u] == response
        assert response.request_info.headers["User-Agent"]


async def test_get_page_with_user_agent():
    async with ClientSession() as s:
        u = Url(url="https://www.example.com", user_agent="blabla")

        response = await get_page(s=s, url=u)

        assert urls_and_responses[u] == response
        assert response.request_info.headers["User-Agent"] == "blabla"


async def test_run_without_user_agent():
    stop_event = asyncio.Event()

    u = Url(url="https://www.example.com")

    urls_and_responses[u] = None

    stop_event.set()

    # Run task in background without waiting for it
    asyncio.create_task(run(stop_event))

    await asyncio.sleep(3)

    response = urls_and_responses[u]
    assert response is not None
    assert response.request_info.headers["User-Agent"]


async def test_run_with_user_agent():
    stop_event = asyncio.Event()
    user_agent = "fake-user-agent"

    u = Url(url="https://www.example.org", user_agent=user_agent)

    urls_and_responses[u] = None

    stop_event.set()

    # Run task in background without waiting for it
    asyncio.create_task(run(stop_event))

    await asyncio.sleep(3)

    response = urls_and_responses[u]
    assert response is not None
    assert response.request_info.headers["User-Agent"] == user_agent

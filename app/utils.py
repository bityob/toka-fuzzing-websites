from asyncio.exceptions import CancelledError
import inspect
from functools import wraps
import logging
from typing import Dict, List, Optional, Callable, Any
import uuid

import asyncio
import aiohttp
# Need to update fake_useragent/utils.py file manually because of known bug
# See: https://github.com/hellysmile/fake-useragent/pull/110/files
from fake_useragent import UserAgent
from pydantic import BaseModel



USER_AGENT_HEADER = "User-Agent"


class Url(BaseModel):
    url: str
    user_agent: Optional[str]

    def __hash__(self):
        return hash(self.url)

    def __id__(self):
        return self.url

    def __eq__(self, other):
        return self.url == other.url

    def __str__(self):
        return self.url



ua = UserAgent()
urls_and_responses: Dict[Url, Optional[aiohttp.ClientResponse]] = dict()
logger = logging.getLogger(__name__)


async def get_page(s: aiohttp.ClientSession, url: Url):
    if url.user_agent:
        # If url class has a specific user agent - use it,
        # else use the session global value

        # Copy session headers to not update the global headers value
        hedears = s.headers.copy()
        hedears[USER_AGENT_HEADER] = url.user_agent
        
        response = await s.get(url=url.url, headers=hedears)
    else:
        # Must pass the headers here explicit so we can test in the tests 
        response = await s.get(url=url.url, headers=s.headers)

    urls_and_responses[url] = response

    return response


async def handle_url(task_id: str, s: aiohttp.ClientSession, url: Url) -> aiohttp.ClientResponse:
    print(f"[{task_id}] Handling url... {url}")
    
    response = await get_page(s, url)

    print(f"[{task_id}] Response: {response.status},\nUser-Agent: {response.request_info.headers[USER_AGENT_HEADER]}")

    return response

async def fetch_urls(task_id: str, user_agent: str = None):
    if user_agent is None:
        user_agent = ua.random

    async with aiohttp.ClientSession() as s:
        s.headers[USER_AGENT_HEADER] = user_agent

        tasks = []

        for url in urls_and_responses:
            task = asyncio.create_task(handle_url(task_id=task_id, s=s, url=url))
            tasks.append(task)

        return await asyncio.gather(*tasks)


def background_task_wrapper(func: Callable) -> Callable:
    """
    Source: https://johachi.hashnode.dev/important-gotchas-with-backgroundtasks-in-fastapi
    """
    task_name = func.__name__

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> None:
        task_id = uuid.uuid4()
        kwargs["task_id"] = task_id

        func_args = inspect.signature(func).bind(*args, **kwargs).arguments
        func_args_str = (
            ", ".join("{}={!r}".format(*item) for item in func_args.items())
        )

        print(
            f"[{task_id}] Started {task_name} with arguments: {func_args_str}"
        )

        try:
            await func(*args, **kwargs)
            print(f"[{task_id}] Finished {task_name} Successfully")
        except CancelledError:
            print(
            f"[{task_id}] Cancelded... {task_name}"
            )
        except Exception as e: #4
            print(
            f"[{task_id}] Failed Permanently {task_name} with error: {e}"
            )
            # 5

    return wrapper

    
@background_task_wrapper
async def run(stop_event: asyncio.Event, task_id: str, user_agent: str = None):
    while True:
        await fetch_urls(task_id, user_agent)
        
        if stop_event.is_set():
            return

        print(f"[{task_id}] Sleeping...")
        await asyncio.sleep(10)
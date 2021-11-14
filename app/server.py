import asyncio
from typing import List

import aiohttp
from fastapi import FastAPI, BackgroundTasks, Response


from app.utils import (
    USER_AGENT_HEADER,
    run as run_fetch_urls,
    Url,
    urls_and_responses,
    handle_url,
    ua,
)


app = FastAPI()
stop_event = None


def safe_delete(url: Url) -> bool:
    try:
        del urls_and_responses[url]
        return True
    except KeyError:
        return False


@app.post("/run")
async def run(urls: List[Url], background_tasks: BackgroundTasks):
    global stop_event

    if stop_event:
        # Stop running tasks
        stop_event.set()

    # Set new event for next tasks
    stop_event = asyncio.Event()

    # Clear all urls and add the new ones
    urls_and_responses.clear()

    urls_and_responses.update({url: None for url in urls})

    # Add new running for received urls
    background_tasks.add_task(run_fetch_urls, stop_event)

    return "Run urls in background"


@app.post("/run_once")
async def run_once(url: Url):
    async with aiohttp.ClientSession() as s:
        if url.user_agent is None:
            url.user_agent = ua.random

        s.headers[USER_AGENT_HEADER] = url.user_agent
        response = await handle_url(task_id=None, s=s, url=url)

    return await response.text()


@app.post("/add_url")
async def add_url(url: Url, response: Response):
    # Must remove it first, because we want to have the updated user-agent
    # which is not part of the id/equality of the class
    safe_delete(url)
    urls_and_responses[url] = None
    return "OK"


@app.post("/remove_url")
async def remove_url(url: Url, response: Response):
    result = safe_delete(url)

    if not result:
        response.status_code = 404
        return "No such url"

    return "OK"


@app.get("/get_last_response")
async def get_last_response(url: Url, response: Response):
    try:
        response = urls_and_responses[url]
        return await response.text()
    except KeyError:
        response.status_code = 404
        return "No such url"

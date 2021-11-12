from typing import List

import asyncio
import aiohttp
import click

from app.utils import run, Url, urls_and_responses

# See https://stackoverflow.com/a/66772223
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())



@click.command()
@click.option('--url', multiple=True, help='Urls to query', prompt='The url/s to query')
@click.option('--user-agent', default=None, 
              help='User agent to use, if not defined will use a random one')
def service_commmand(url: List[str], user_agent: str):
    if not url:
        raise RuntimeError("Url is not defined")

    urls = url

    urls_and_responses.update(
        {Url(url=url): None for url in urls}
    )
    
    asyncio.run(run(stop_event=asyncio.Event(), user_agent=user_agent))


if __name__ == "__main__":
    service_commmand()
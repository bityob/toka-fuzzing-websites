from typing import List

import asyncio
import aiohttp
import click
# Need to update fake_useragent/utils.py file manually because of known bug
# See: https://github.com/hellysmile/fake-useragent/pull/110/files
from fake_useragent import UserAgent


USER_AGENT_HEADER = "User-Agent"

# See https://stackoverflow.com/a/66772223
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
ua = UserAgent()


async def get_page(s, url):
    return await s.get(
        url=url,
    )    


async def handle_url(s, url):
    print(f"Handling url... {url}")
    
    response = await get_page(s, url)

    print(f"Response: {response},\nUser-Agent: {response.request_info.headers[USER_AGENT_HEADER]}")


async def run(urls, user_agent=None):
    if user_agent is None:
        user_agent = ua.random
        
    async with aiohttp.ClientSession() as s:
        s.headers[USER_AGENT_HEADER] = user_agent

        tasks = []
        
        for url in urls:
            task = asyncio.create_task(handle_url(s=s, url=url))
            tasks.append(task)

        return await asyncio.gather(*tasks)


@click.command()
@click.option('--url', multiple=True, help='Urls to query', prompt='The url/s to query')
@click.option('--user-agent', default=None, 
              help='User agent to use, if not defined will use a random one')
def service_commmand(url: List[str], user_agent: str):
    if not url:
        raise RuntimeError("Url is not defined")

    # loop = asyncio.get_event_loop()
    # urls = [*url] * 30
    urls = url
    # loop.run_until_complete(run(urls=urls, user_agent=user_agent))
    asyncio.run(run(urls=urls, user_agent=user_agent))


if __name__ == "__main__":
    service_commmand()
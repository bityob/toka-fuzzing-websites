from typing import List

import asyncio
import asyncclick as click


from app.utils import run, Url, urls_and_responses

# See https://stackoverflow.com/a/66772223
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
stop_event = None


@click.command()
@click.option('--url', multiple=True, help='Urls to query', prompt='The url/s to query')
@click.option('--user-agent', default=None, 
              help='User agent to use, if not defined will use a random one')
async def service_commmand(url: List[str], user_agent: str):
    global stop_event

    if not url:
        raise RuntimeError("Url is not defined")

    urls = url

    urls_and_responses.update(
        {Url(url=url): None for url in urls}
    )
    
    if stop_event is None:
        stop_event = asyncio.Event()

    await run(stop_event=stop_event, user_agent=user_agent)


if __name__ == "__main__":
    try:
        service_commmand(_anyio_backend="asyncio", standalone_mode=False)
    except KeyboardInterrupt:
        print("Aborted!")
from concurrent.futures import ThreadPoolExecutor, as_completed

import click
from fake_useragent import UserAgent
from requests import Session


USER_AGENT_HEADER = "User-Agent"

s = Session()
ua = UserAgent()


def get_page(url):
    return s.get(
        url=url,
    )    


def handle_url(url):
    print(f"Handling url... {url}")
    
    response = get_page(url)

    print(f"Response: {response},\nUser-Agent: {response.request.headers[USER_AGENT_HEADER]}")


def run(urls, user_agent=None):
    if user_agent is None:
        user_agent = ua.random
    
    s.headers[USER_AGENT_HEADER] = user_agent
    
    with ThreadPoolExecutor() as executor:
        futures = []
        
        for url in urls:
            futures.append(executor.submit(handle_url, url=url))
        
        for future in as_completed(futures):
            future.result()


@click.command()
@click.option('--url', multiple=True, help='Urls to query', prompt='The url/s to query')
@click.option('--user-agent', default=None, 
              help='User agent to use, if not defined will use a random one')
def service_commmand(url, user_agent):
    if not url:
        raise RuntimeError("Url is not defined")

    run(urls=url, user_agent=user_agent)


if __name__ == "__main__":
    # urls = [
    #     "https://www.example.com",
    #     "https://httbin.org",
    # ]
    service_commmand()
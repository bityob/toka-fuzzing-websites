from fake_useragent import UserAgent
from requests import Session


USER_AGENT_HEADER = "User-Agent"

s = Session()
ua = UserAgent()


def get_page(url):
    s.headers[USER_AGENT_HEADER] = ua.random

    return s.get(
        url=url,
    )    


def handle_url(url):
    print(f"Handling url... {url}")
    
    response = get_page(url)

    print(f"Response: {response},\nUser-Agent: {response.request.headers[USER_AGENT_HEADER]}")


def main(urls):
    for url in urls:
        handle_url(url)


if __name__ == "__main__":
    urls = [
        "https://www.example.com",
        "https://httbin.org",
    ]

    main(urls)
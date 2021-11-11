from fake_useragent import UserAgent
from requests import Session

s = Session()
ua = UserAgent()


def get_page(url):
    s.headers["User-Agent"] = ua.random

    return s.get(
        url=url,
    )    


def main():
    
    response = get_page("https://www.example.com")

    print(response)
    print(response.request.headers)

if __name__ == "__main__":
    main()
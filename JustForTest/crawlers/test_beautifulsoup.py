import time
import requests
from bs4 import BeautifulSoup


def request(url):
    response = requests.get(url)
    return response.content


def parser(content):
    start = time.time()
    soup = BeautifulSoup(content, "html.parser")
    text = soup.get_text()
    # print text
    end = time.time()
    print (end - start) * 1000


if __name__ == '__main__':
    start = time.time()
    for i in range(1, 100):
        request('https://www.nowcoder.com/discuss/3043?type=0&order=0&pos=7&page=6')
    end = time.time()

    print end - start


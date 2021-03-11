import requests
from bs4 import BeautifulSoup


class HBON:
    def __init__(self):
        self.request = requests.session()
        self._headers = {

        }

    def parser(self):
        pass


if __name__ == '__main__':
    print('ok')
    headers = {
        'cookie': 'MoodleSession=ejbhbvgl9jdm184s5ogvpm0rrj'
    }
    res = requests.get('https://hocbaionha.com/mod/quiz/attempt.php?attempt=906017&cmid=568',
                       headers=headers)
    with open('page.html', 'w') as f:
        f.write(res.text)

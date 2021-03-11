import json
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup

if __name__ == '__main__':
    headers = {
        'cookie': 'MoodleSession=ejbhbvgl9jdm184s5ogvpm0rrj'
    }

    with open('course.json', 'r') as f:
        data = []
        courses = json.load(f)
        for course_href in courses:
            course_dict = {
                'url': urljoin('https://hocbaionha.com', course_href['url']),
                'course_items': []
            }
            resp = requests.get(course_dict['url'], headers=headers)
            soup = BeautifulSoup(resp.text, 'html.parser')
            course_block = soup.select_one('.course-block')
            if not course_block:
                continue
            header = course_block.select_one('div > a')
            course_item = {
                'url': urljoin('https://hocbaionha.com', header.get('href')),
                'lessons': []
            }
            resp = requests.get(course_item['url'], headers=headers)
            soup = BeautifulSoup(resp.text, 'html.parser')
            for topic in soup.select('#region-main > div > div > ul > li'):
                section = topic.select_one('.content > h3')
                section_dict = {
                    'name': section.text,
                    'url': section.select_one('a').get('href'),
                    'content': []
                }
                section_detail = topic.select_one('.content > ul')
                if not section_detail:
                    continue
                for _item in section_detail.select('.activityinstance'):
                    url = _item.select_one('a').get('href')
                    name = _item.select_one('.instancename').text
                    section_dict['content'].append({
                        'name': name,
                        'url': url
                    })
                course_item['lessons'].append(section_dict)
            course_dict['course_items'].append(course_item)
            data.append(course_dict)
        with open('index.json', 'w') as fd:
            fd.write(json.dumps(data))

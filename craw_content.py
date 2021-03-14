import os
import json
import re
import shlex
import subprocess

import requests
import urllib.parse as urlparse
from urllib.parse import parse_qs

s1 = u'ÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚÝàáâãèéêìíòóôõùúýĂăĐđĨĩŨũƠơƯưẠạẢảẤấẦầẨẩẪẫẬậẮắẰằẲẳẴẵẶặẸẹẺẻẼẽẾếỀềỂểỄễỆệỈỉỊịỌọỎỏỐốỒồỔổỖỗỘộỚớỜờỞởỠỡỢợỤụỦủỨứỪừỬửỮữỰựỲỳỴỵỶỷỸỹ'
s0 = u'AAAAEEEIIOOOOUUYaaaaeeeiioooouuyAaDdIiUuOoUuAaAaAaAaAaAaAaAaAaAaAaAaEeEeEeEeEeEeEeEeIiIiOoOoOoOoOoOoOoOoOoOoOoOoUuUuUuUuUuUuUuYyYyYyYy'


def normalize_file_name(input_str):
    s = ''
    for c in input_str:
        if c in s1:
            s += s0[s1.index(c)]
        else:
            s += c
    s = " ".join(s.split()).replace(' ', '_')
    s = re.sub('[^a-zA-Z0-9_*]', '', s).lower()
    return s


class Content:
    def __init__(self, session_key):
        self.session_key = session_key
        self._headers = {
            'cookie': f'MoodleSession={self.session_key};'
        }

    def get_sesskey(self, quiz_url):
        headers = self._headers.copy()
        resp = requests.get(url=quiz_url, headers=headers)

        pattern = re.compile(r"M.cfg = ({.*?});",
                             re.MULTILINE | re.DOTALL)
        search_pattern = pattern.search(resp.text)
        m_cfg = search_pattern.group(0).replace('M.cfg = ', '').replace(';', '')
        m_cfg_dict = json.loads(m_cfg)
        return m_cfg_dict['sesskey']

    def start_quiz(self, sesskey, cmid):
        command = f"""
        curl --location --request POST 'https://hocbaionha.com/mod/quiz/startattempt.php' \
    --header 'cookie: MoodleSession={self.session_key};' \
    --header 'Content-Type: application/x-www-form-urlencoded' \
    --data-urlencode 'cmid={cmid}' \
    --data-urlencode 'sesskey={sesskey}'
        """
        args = shlex.split(command)
        process = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        html_text = stdout.decode('utf-8')
        with open('page.html', 'w') as f:
            f.write(html_text)
        pattern = re.compile(r'"https://hocbaionha.com/mod/quiz/attempt.php\?attempt=(.*?)"',
                             re.MULTILINE | re.DOTALL)
        search_pattern = pattern.search(html_text)
        if not search_pattern:
            pattern = re.compile(r'"https://hocbaionha.com/mod/quiz/summary.php\?attempt=(.*?)"',
                                 re.MULTILINE | re.DOTALL)
            search_pattern = pattern.search(html_text)
        if search_pattern:
            attempt_url = search_pattern.group(0).replace('"', '')
            parsed = urlparse.urlparse(attempt_url)
            return parse_qs(parsed.query)['attempt'][0]
        else:
            return self.start_quiz_exam(sesskey, cmid)

    def start_quiz_exam(self, sesskey, cmid):
        command = f"""
        curl --location --request POST 'https://hocbaionha.com/mod/quiz/startattempt.php' \
    --header 'cookie: MoodleSession={self.session_key};' \
    --header 'Content-Type: application/x-www-form-urlencoded' \
    --data-urlencode 'cmid={cmid}' \
    --data-urlencode 'sesskey={sesskey}' \
    --data-urlencode '_qf__mod_quiz_preflight_check_form=1' \
    --data-urlencode 'submitbutton=Bắt+đầu+làm+bài'
        """
        print(command)
        args = shlex.split(command)
        process = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        html_text = stdout.decode('utf-8')
        with open('page.html', 'w') as f:
            f.write(html_text)
        pattern = re.compile(r'"https://hocbaionha.com/mod/quiz/attempt.php\?attempt=(.*?)"',
                             re.MULTILINE | re.DOTALL)
        search_pattern = pattern.search(html_text)
        if not search_pattern:
            pattern = re.compile(r'"https://hocbaionha.com/mod/quiz/summary.php\?attempt=(.*?)"',
                                 re.MULTILINE | re.DOTALL)
            search_pattern = pattern.search(html_text)
        attempt_url = search_pattern.group(0).replace('"', '')
        parsed = urlparse.urlparse(attempt_url)
        return parse_qs(parsed.query)['attempt'][0]

    def finish_quiz(self, sesskey, attempt, cmid, fpath):
        command = f"""
        curl --location --request POST 'https://hocbaionha.com/mod/quiz/processattempt.php' \
    --header 'cookie: MoodleSession={self.session_key};'\
    --header 'Content-Type: application/x-www-form-urlencoded' \
    --data-urlencode 'attempt={attempt}' \
    --data-urlencode 'finishattempt=1' \
    --data-urlencode 'timeup=60' \
    --data-urlencode 'slots=' \
    --data-urlencode 'cmid={cmid}' \
    --data-urlencode 'sesskey={sesskey}'
        """

        args = shlex.split(command)
        process = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        html_text = stdout.decode('utf-8')
        with open(fpath, 'w') as f:
            f.write(html_text)

    def crawl_quiz(self, quiz_url: str, fpath: str):
        parsed = urlparse.urlparse(quiz_url)
        cmid = parse_qs(parsed.query)['id'][0]
        sesskey = self.get_sesskey(quiz_url)
        attempt = self.start_quiz(sesskey, cmid)
        self.finish_quiz(sesskey, attempt, cmid, fpath)

    def craw_content(self, url: str, fpath: str):
        command = f"""
        curl --location --request GET '{url}' \
    --header 'cookie: MoodleSession={self.session_key};'
        """
        args = shlex.split(command)
        process = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        try:
            html_text = stdout.decode('utf-8')
            with open(fpath, 'w') as f:
                f.write(html_text)
        except UnicodeDecodeError:
            with open(fpath, 'w') as f:
                f.write(command)


if __name__ == '__main__':
    crawl = Content(session_key='vm3qb73bop414dt76ouumdet3r')
    with open('index.json') as f:
        data = json.load(f)
    for course in data:
        course_name = course['name'].lower().replace(' ', '_')
        lessons = course['lessons']
        for lesson in lessons:
            lesson_name = normalize_file_name(lesson['name'])
            for item in lesson['content']:
                fname = normalize_file_name(item['name']) + '.html'
                fpath = os.path.join('data', course_name, lesson_name, fname)
                os.makedirs(os.path.dirname(fpath), exist_ok=True)
                item_url = item['url']
                if os.path.isfile(fpath):
                    print(f'crawled: {fpath}')
                    continue
                if 'quiz' in item_url:
                    print(item_url)
                    crawl.crawl_quiz(item_url, fpath)
                else:
                    crawl.craw_content(item_url, fpath)
                print(f'crawled: {fpath}')

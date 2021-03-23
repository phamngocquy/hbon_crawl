import json
import re
import shlex
import subprocess

import requests
import urllib.parse as urlparse
from urllib.parse import parse_qs

HEADERS = {
    'cookie': 'MoodleSession=fl9ldqjbuo8iglas52igvmltcg;'
}


# get sesskey
# resp = requests.get(url=quiz_url, headers=headers)
# soup = BeautifulSoup(resp.text, 'html.parser')
# pattern = re.compile(r"M.cfg = ({.*?});",
#                      re.MULTILINE | re.DOTALL)
# search_pattern = pattern.search(resp.text)
# m_cfg = search_pattern.group(0).replace('M.cfg = ', '').replace(';', '')
# m_cfg_dict = json.loads(m_cfg)

# start attempt
# payload = {
#     'cmid': '21',
#     'sesskey': m_cfg_dict['sesskey']
# }


def get_sesskey(quiz_url):
    resp = requests.get(url=quiz_url, headers=HEADERS)
    pattern = re.compile(r"M.cfg = ({.*?});",
                         re.MULTILINE | re.DOTALL)
    search_pattern = pattern.search(resp.text)
    m_cfg = search_pattern.group(0).replace('M.cfg = ', '').replace(';', '')
    m_cfg_dict = json.loads(m_cfg)
    return m_cfg_dict['sesskey']


def start_quiz(sesskey, cmid):
    command = f"""
    curl --location --request POST 'https://hocbaionha.com/mod/quiz/startattempt.php' \
--header 'cookie: MoodleSession=fl9ldqjbuo8iglas52igvmltcg;' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data-urlencode 'cmid={cmid}' \
--data-urlencode 'sesskey={sesskey}'
    """.format(cmid=cmid, sesskey=sesskey)
    args = shlex.split(command)
    process = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    html_text = stdout.decode('utf-8')
    with open('page2.html', 'w') as f:
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


def finish_quiz(sesskey, attempt, cmid):
    command = f"""
    curl --location --request POST 'https://hocbaionha.com/mod/quiz/processattempt.php' \
--header 'cookie: MoodleSession=fl9ldqjbuo8iglas52igvmltcg;'\
--header 'Content-Type: application/x-www-form-urlencoded' \
--data-urlencode 'attempt={attempt}' \
--data-urlencode 'finishattempt=1' \
--data-urlencode 'timeup=60' \
--data-urlencode 'slots=' \
--data-urlencode 'cmid={cmid}' \
--data-urlencode 'sesskey={sesskey}'
    """.format(attempt=attempt, cmid=cmid, sesskey=sesskey)

    args = shlex.split(command)
    process = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    html_text = stdout.decode('utf-8')
    with open('page3.html', 'w') as f:
        f.write(html_text)


def content():
    command = """
    curl --location --request GET 'https://hocbaionha.com/mod/wiki/view.php?id=4684' \
--header 'cookie: MoodleSession=fl9ldqjbuo8iglas52igvmltcg;'
    """
    args = shlex.split(command)
    process = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    html_text = stdout.decode('utf-8')
    with open('page4.html', 'w') as f:
        f.write(html_text)


if __name__ == '__main__':
    # quiz_url = 'https://hocbaionha.com/mod/quiz/view.php?id=25'php
    # cmid = 25
    # sesskey = get_sesskey(quiz_url)
    # attempt = start_quiz(sesskey, cmid)
    #
    # print(sesskey, attempt, cmid)
    # finish_quiz(sesskey, attempt, cmid)
    content()

# resp = requests.post(url=start_attempt_url, headers=headers, data=payload)
#
# print(resp.headers)
#
# print(resp.status_code)
# print(resp.request.body)
# print(resp.request.headers)
# print(resp.request.url)
#
# resp = requests.post(url=resp.request.url, headers=resp.request.headers)
# with open('page2.html', 'w') as f:
#     f.write(stdout.decode('utf-8'))
# print(resp.status_code)

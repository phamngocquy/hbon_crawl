import os
import glob
import boto3
import string
import random
import mimetypes
from io import BytesIO
from copy import copy

import requests
from enum import Enum
from bs4 import BeautifulSoup

REMOVE_ATTRIBUTES = [
    'lang', 'language', 'onmouseover', 'onmouseout', 'script', 'style', 'font',
    'dir', 'face', 'size', 'color', 'style', 'class', 'width', 'height',
    'hspace',
    'border', 'valign', 'align', 'background', 'bgcolor', 'cellpadding',
    'cellspacing',
    'class', 'id', 'name', 'type', 'value', 'for', 'disabled', 'class']


class CourseType(Enum):
    MATH = 'math'


class Parser:
    def __init__(self, session_key=None):
        self.session_key = session_key
        self._headers = {
            'cookie': f'MoodleSession={self.session_key};'
        }
        self.raw_data = []
        self.root_path = 'data/*/*/*'

    def add_course_type(self):
        files = glob.glob(self.root_path)
        for file in files:
            course_name = file.split(os.sep)[1]
            if course_name.startswith('dai_so') \
                    or course_name.startswith('so_hoc'):
                self.raw_data.append((file, CourseType.MATH))

    @staticmethod
    def _parser_math_quiz(file):
        soup = BeautifulSoup(open(file, 'r').read(), 'html.parser')
        questions_data, tips_data = [], []
        questions_tag = soup.select("div[id^=question-]")
        for item in questions_tag:
            qtext = item.select_one("div[class=qtext]")
            try:
                answers = [[item.text.strip(), False] for item in
                           item.select_one("div[class=answer]").select(
                               "div[class^=r]") if item.text]
                r_answers = [item.text for item in
                             item.select("div[class=rightanswer]")]
                for answer in answers:
                    if any(answer[0] in r_item for r_item in r_answers):
                        answer[1] = True
                questions_data.append((qtext, answers))
            except AttributeError:
                if qtext:
                    tips_data.append(qtext)
        for item in questions_data:
            print(item)
            print('##########')
        print(tips_data)

    @staticmethod
    def _parser_math_theory(file):
        soup = BeautifulSoup(open(file, 'r').read(), 'html.parser')
        item = soup.select_one('div[class=no-overflow]')
        with open('page.html', 'w') as f:
            f.write(str(item))

    def parser_math(self, file):
        if os.path.basename(file).startswith('luyen_tap'):
            self._parser_math_quiz(file)
        elif os.path.basename(file).startswith('ly_thuyet'):
            self._parser_math_theory(file)

    def parser(self):
        for item in self.raw_data:
            if item[1] == CourseType.MATH:
                self.parser_math(
                    '/home/qpham/IProject/hbon_crawl/data/dai_so_9/_25_he_so_goc_cua_duong_thang_yaxb_a_neq_0/ly_thuyet_he_so_goc_cua_duong_thang_yaxb_a_neq_0_wiki.html')
                # self.parser_math(item[0])
                break

    def store_image_2s3(self, bucket_name, image_url):

        # dload image file
        headers = copy(self._headers)
        resp = requests.get(url=image_url, headers=headers)

        # fpath
        image_suffix = image_url[image_url.rfind('.'):]
        image_name = ''.join(random.choices(
            string.ascii_uppercase + string.digits, k=8)
        ) + image_suffix

        fpath = f'/{image_name}'
        content_type = mimetypes.guess_type(fpath)[0]

        # upload object to s3
        image_obj = BytesIO(resp.content)
        s3 = boto3.resource(service_name='s3')
        s3.Bucket(bucket_name).upload_fileobj(Fileobj=image_obj, Key=fpath,
                                              ExtraArgs={"ACL": "public-read",
                                                         "ContentType": content_type})
        return f'https://{bucket_name}.s3.amazonaws.com/{fpath}'

    @staticmethod
    def clean_html(html_tag):
        for attribute in REMOVE_ATTRIBUTES:
            for tag in html_tag.find_all(attrs={attribute: True}):
                del tag[attribute]
        return html_tag

    def run(self):
        self.add_course_type()
        self.parser()


if __name__ == '__main__':
    Parser().run()

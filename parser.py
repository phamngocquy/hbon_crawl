import mimetypes
import os
import glob
from io import BytesIO
import json
import logging
import random
import string
from copy import copy
import boto3

import requests
from enum import Enum
from bs4 import BeautifulSoup


class CourseType(Enum):
    MATH = 'math'


class Parser:
    def __init__(self, session_key):
        self.session_key = session_key
        self._headers = {
            'cookie': f'MoodleSession={self.session_key};'
        }
        self.raw_data = []
        self.root_path = '/Users/phamngocquy/PycharmProjects/hbon/data/*/*/*'

    def add_course_type(self):
        files = glob.glob(self.root_path)
        for file in files:
            course_name = file.split(os.sep)[6]
            if course_name.startswith('dai_so') \
                    or course_name.startswith('so_hoc'):
                self.raw_data.append((file, CourseType.MATH))

    def _parser_math(self, file):
        file = '/Users/phamngocquy/PycharmProjects/hbon/data/dai_so_7/_11_tap_hop_q_cac_so_huu_ti/luyen_tap_tap_hop_q_cac_so_huu_ti_de_thi.html'
        content = open(file, 'r')
        soup = BeautifulSoup(content.read(), 'html.parser')
        if os.path.basename(file).startswith('luyen_tap'):
            questions = soup.select("div[id^=question-]")

            # parser qtext
            for item in questions:
                # question - qtext
                qtext = item.select_one("div[class=qtext]")

                # question
                pass

            pass

    def _qtext_parser(self):
        pass

    def parser(self):
        for item in self.raw_data:
            if item[1] == CourseType.MATH:
                self._parser_math(item[0])
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

    def run(self):
        self.add_course_type()
        self.parser()


if __name__ == '__main__':
    pass
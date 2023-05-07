import os

import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder


def upload_test(filename):
    url = 'http://localhost:80'
    MultipartEncoder(
        fields={
            'api-key': 'test', # 파일 외 API 에서 요구하는 form data
            'file_data': (os.path.basename(filename), open(filename, 'rb'), 'image')
        }
    )
    headers = {'Content-type': body.content_type}
    response = requests.post(url, headers=headers, data=body)
    return response
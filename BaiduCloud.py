# encoding:utf-8
import requests

'''
通用文字识别
'''
APP_KEY = 'rXGQpX6DIavNqVoVMZ7r3804'
SECRET_KEY = 'yWwxn889WFjaR2P14AM1HVn60a4jGPMD'

class BaiduOCR(object):
    def __init__(self, AKey, SKey):
        self.app_key = AKey
        self.secret_key = SKey
    
    def get_access_token(self):
        host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={}&client_secret={}'.format(self.app_key, self.secret_key)
        response = requests.get(host)
        if response:
            resjson = response.json()
            if resjson['access_token']:
                return resjson['access_token']
            else:
                print('access_token error!')
    
    def basic(self, img_b64):
        request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic"
        data = {"image": img_b64, 'language_type': 'CHN_ENG'}
        access_token = self.get_access_token()
        request_url = request_url + "?access_token=" + access_token
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        response = requests.post(request_url, data = data, headers = headers)
        if response:
            # resjson = response.json()
            print (response.json())
            # word = resjson['words_result'][0]['words'].replace(' ', '')
            # return word
    
    def basic_location(self, img_b64):
        request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/general"
        params = {"image":img_b64, 'language_type': 'CHN_ENG', 'recognize_granularity': 'small', 'detect_direction': 'true'}
        access_token = self.get_access_token()
        request_url = request_url + "?access_token=" + access_token
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        response = requests.post(request_url, data=params, headers=headers)
        if response:
            print (response.json())
    
    def accurate_location(self, img_b64):
        request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate"
        params = {"image":img_b64, 'language_type': 'CHN_ENG', 'recognize_granularity': 'small', 'detect_direction': 'true'}
        access_token = self.get_access_token()
        request_url = request_url + "?access_token=" + access_token
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        response = requests.post(request_url, data=params, headers=headers)
        if response:
            print (response.json())

baidu = BaiduOCR(APP_KEY, SECRET_KEY)
with open('1.txt', 'r+', encoding = 'utf-8') as f:
    b64 = f.read()
baidu.accurate_location(b64)
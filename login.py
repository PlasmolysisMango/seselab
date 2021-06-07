from spider_base import *
import requests
import re
import base64
import pytesseract
from PIL import Image
from io import BytesIO
import time

APP_KEY = 'rXGQpX6DIavNqVoVMZ7r3804'
SECRET_KEY = 'yWwxn889WFjaR2P14AM1HVn60a4jGPMD'

def res2cookie(response):
    cookies = requests.utils.dict_from_cookiejar(response.cookies)
    return cookies

class TongjiLogin(object):
    def __init__(self):
        self.uid_list = []
        self.psw_list = []
        with open('account.txt', 'r') as f:
            for line in f:
                self.uid_list.append(line.split()[0])
                self.psw_list.append(line.split()[1])
        h = '''
        Host: seselab.tongji.edu.cn
Connection: keep-alive
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
Sec-Fetch-Site: same-site
Sec-Fetch-Mode: navigate
Sec-Fetch-Dest: document
sec-ch-ua: "Google Chrome";v="87", " Not;A Brand";v="99", "Chromium";v="87"
sec-ch-ua-mobile: ?0
Referer: https://ids.tongji.edu.cn:8443/
Accept-Encoding: gzip, deflate, br
Accept-Language: zh-CN,zh;q=0.9
'''
        self.headers = get_headersDict(h)
        self.mode = 'baidu_ocr' # 三种识别模式：tesseract, baidu_ocr, 人工输入
    
    def img2code(self, headers, cookies, mode = 'baidu_ocr'):
        url = 'https://ids.tongji.edu.cn:8443/nidp/app/login?sid=0&sid=0&flag=true'
        img_b64 = getHTMLText(url, headers = headers, cookies = cookies).split(';base64,')[1]
        img_content = base64.b64decode(img_b64) # 转成byte格式
        # with open('code.jpg', 'wb') as f:
            # f.write(img_content) # 保存原始验证码文件
        img_file = BytesIO(img_content)
        img = Image.open(img_file)
        if mode == 'tesseract': 
            img = img.convert('RGB')
            pixdata = img.load()
            for y in range(img.size[1]): # 图片二值化
                for x in range(img.size[0]):
                    if pixdata[x, y][0] < 240:
                        pixdata[x, y] = (0, 0, 0)
                    if pixdata[x, y][1] < 240:
                        pixdata[x, y] = (0, 0, 0)
                    if pixdata[x, y][2] < 240:
                        pixdata[x, y] = (0, 0, 0)
            code = pytesseract.image_to_string(img, lang = 'eng')
        elif mode == 'baidu_ocr':
            code = baidu_ocr.read(img_b64)
        elif mode == 'manual': 
            img.show()
            code = input('请输入验证码：')
        return code
    
    def login(self, uid, psw):
        url = 'https://seselab.tongji.edu.cn/api/login'
        r1 = requests.get(url, allow_redirects = False)
        php_cookies = res2cookie(r1) # 获取PHPSESSID
        url2 = 'https://seselab.tongji.edu.cn/sso/'
        r2 = requests.get(url2, cookies = php_cookies)
        url3 = 'https://ids.tongji.edu.cn:8443' + re.search('action="[\s\S]+?"', r2.text).group(0).split('"')[1]
        r3 = requests.get(url3)
        jes_urn_cookies = res2cookie(r3) # 获取JSESSIONID
        url4 = 'https://ids.tongji.edu.cn:8443/nidp/app/login?sid=0&sid=0'
        data = getDict('option=credential&Ecom_User_ID=2030563&Ecom_Password=Htt05j2666&Ecom_code=bufw')
        data['Ecom_User_ID'] = uid
        data['Ecom_Password'] = psw
        self.headers['Referer'] = url3
        times = 1
        while True:    
            try:
                code = self.img2code(headers = self.headers, cookies = jes_urn_cookies, mode = self.mode)
                data['Ecom_code'] = code
                r4 = requests.post(url3, data = data, cookies = jes_urn_cookies, headers = self.headers) # POST登录信息
                jes_cookies = res2cookie(r4) # 获取新的JSESSIONID
                jes_urn_cookies['JSESSIONID'] = jes_cookies['JSESSIONID']
                url5 = re.search('window.location.href=\'[\s\S]+?\'', r4.text).group(0).split('\'')[1]
                if 'tongjiaccount' in url5:
                    print(url5)
                    raise Exception('login_failed')
                elif 'client_id' in url5:
                    break
            except:
                print('登录失败，第{}次重试...'.format(times))
                times += 1
                time.sleep(2)
        self.headers['Referer'] = url4
        r5 = requests.get(url5, headers = self.headers, cookies = jes_urn_cookies)
        token = re.search('"token":"[\s\S]+?"}', r5.text).group(0).split('"')[-2] # 获取到auth信息
        if php_cookies and token:
            print('登录成功！\nPHPSESSID：{}\nAuthorization：{}'.format(php_cookies['PHPSESSID'], token))
        return php_cookies['PHPSESSID'], token # 返回登陆成功的PHPSESSID和Authorization
    
    def switch_account(self, num = 0):
        uid = self.uid_list[num]
        psw = self.psw_list[num]
        phpid, auth = self.login(uid, psw)
        return phpid, auth

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
    
    def read(self, img_b64):
        request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic"
        data = {"image": img_b64, 'language_type': 'ENG'}
        access_token = self.get_access_token()
        request_url = request_url + "?access_token=" + access_token
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        response = requests.post(request_url, data = data, headers = headers)
        if response:
            resjson = response.json()
            word = resjson['words_result'][0]['words'].replace(' ', '')
            return word
            
baidu_ocr = BaiduOCR(APP_KEY, SECRET_KEY) # 实例化

if __name__ == '__main__':
    tongji_login = TongjiLogin()
    tongji_login.mode = 'baidu_ocr'
    tongji_login.switch_account(0)
import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.ocr.v20181119 import ocr_client, models

SecretId = 'AKIDJ9lnZ7NWHoJYw7DqRSGYpHdnmY6EnUGq'
SecretKey = 'VkuqbaPUJuHP3SowDF2auGMRG1Ytz7mC'

class TencentCloud(object):
    def __init__(self, SID, SKEY):
        self.sid = SID
        self.skey = SKEY

    def basic(self, base64code):
        try: 
            cred = credential.Credential(self.sid, self.skey)
            httpProfile = HttpProfile()
            httpProfile.endpoint = "ocr.tencentcloudapi.com"

            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            client = ocr_client.OcrClient(cred, "ap-shanghai", clientProfile) 

            req = models.GeneralBasicOCRRequest()
            params = {
                "ImageBase64": base64code
            }
            req.from_json_string(json.dumps(params))

            resp = client.GeneralBasicOCR(req) 
            print(resp.to_json_string()) 
            with open('d:\\res.txt', 'w+', encoding = 'utf-8') as f:
                f.write(resp.to_json_string())

        except TencentCloudSDKException as err: 
            print(err) 
    
    def accurate(self, base64code):
        try: 
            cred = credential.Credential(self.sid, self.skey)
            httpProfile = HttpProfile()
            httpProfile.endpoint = "ocr.tencentcloudapi.com"

            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            client = ocr_client.OcrClient(cred, "ap-shanghai", clientProfile) 

            req = models.GeneralAccurateOCRRequest()
            params = {
                "ImageBase64": base64code
            }
            req.from_json_string(json.dumps(params))

            resp = client.GeneralAccurateOCR(req) 
            print(resp.to_json_string()) 
            with open('d:\\res.txt', 'w+', encoding = 'utf-8') as f:
                f.write(resp.to_json_string())

        except TencentCloudSDKException as err: 
            print(err) 
    
    def advertise(self, base64code):
        try: 
            cred = credential.Credential(self.sid, self.skey) 
            httpProfile = HttpProfile()
            httpProfile.endpoint = "ocr.tencentcloudapi.com"

            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            client = ocr_client.OcrClient(cred, "ap-shanghai", clientProfile) 

            req = models.AdvertiseOCRRequest()
            params = {
                "ImageBase64": base64code
            }
            req.from_json_string(json.dumps(params))

            resp = client.AdvertiseOCR(req) 
            print(resp.to_json_string()) 
            with open('d:\\res.txt', 'w+', encoding = 'utf-8') as f:
                f.write(resp.to_json_string())

        except TencentCloudSDKException as err: 
            print(err) 

tencent_ocr = TencentCloud(SecretId, SecretKey)
with open('1.txt', 'r+', encoding = 'utf-8') as f:
    b64 = f.read()
tencent_ocr.accurate(b64)


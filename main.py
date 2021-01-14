from spider_base import *
from login import *
import re
import os
from time import sleep, strftime
import random
from urllib.parse import unquote

headers = {}
cookies = {}
cookies2 = {}
uid = None
uid2 = None
medicine = None

def getDict(text, patten = '&', patten2 = '=', stri_patten = ''):
    lis = text.split(patten + stri_patten)
    cookieDict = {}
    for str in lis:
        cookie = str.strip().split(stri_patten + patten2)
        cookieDict[cookie[0].strip(stri_patten)] = cookie[1].strip(stri_patten)
    return cookieDict

def format_med(text):
    f = re.search('\[\{[\s\S]+?\}\]',text).group(0).strip('[]')
    lis = f.split('},{')
    dict_lis = []
    for i in lis:
        tmp = i.strip('{}')
        dic = getDict(tmp, ',', ':', '"')
        dict_lis.append(dic)
    return dict_lis

class Medicine(object):
    def __init__(self, mode = '', total = False, url = '', params = '', s_cookies = {}, page = True):
        self.enable_page = page
        if total:
            self.lis = self.get_medicine(mode)
        else:
            self.lis = self.get_list(url, params, s_cookies)
    
    def get_list(self, url = '', p = '', s_cookies = {}): # 从不同页面获取药品列表
        med_dict_list = []
        page = 1
        oldtext = ''
        while True:
            if not s_cookies:
                s_cookies = cookies
            if p == 'none':
                params = {}
            elif not p:
                p = 'page=1&lx=1&listRows=100'
                params = getDict(p, '&', '=')
            else:
                params = getDict(p, '&', '=')
            text = getHTMLText(url, headers = headers, params = params, cookies = s_cookies)
            if '"data":[]' in text:
                break
            if text == oldtext:
                break
            else:
                oldtext = text
            med_dict_list.extend(format_med(text))
            if not self.enable_page:
                break
            page += 1
            params['page'] = page
        return med_dict_list

    
    def get_medicine(self, mode = ''): # 获取全部药品，并输出至medicine.txt
        file_path = os.path.join('medicine.txt')
        med_dict_list = []
        if not os.path.exists(file_path) or mode == 'new':
            url = 'https://seselab.tongji.edu.cn/api/admin-api/hxp'
            p = 'page=1&lx=1&listRows=100'
            page = 1
            params = getDict(p, '&', '=')
            while True:
                text = getHTMLText(url, headers = headers, params = params, cookies = cookies)
                if '"data":[]' in text:
                    break
                med_dict_list.extend(format_med(text))
                print('page{} done!'.format(page))
                page += 1
                params['page'] = page
            with open(file_path, 'w', encoding = 'utf-8') as f:
                for each in med_dict_list:
                    tmp_str = (each['id'] + ' $ ' + each['title'] + ' $ ' + each['aliasTitle']
                                + ' $ ' + each['enTitle'] + ' $ ' + each['CAS'] + ' $ ' + each['classify_title']
                                + ' $ ' + each['level_title'] + ' $ ' + each['type_title'])
                    f.write(tmp_str + '\n')
        elif os.path.exists(file_path):
            with open(file_path, 'r', encoding = 'utf-8') as f:
                for line in f:
                    dic = {}
                    lis = line.split(' $ ')
                    dic['id'] = lis[0]
                    dic['title'] = lis[1]
                    dic['aliasTitle'] = lis[2]
                    dic['enTitle'] = lis[3]
                    dic['CAS'] = lis[4]
                    dic['classify_title'] = lis[5]
                    dic['level_title'] = lis[6]
                    dic['type_title'] = lis[7]
                    med_dict_list.append(dic)
        if med_dict_list:
            return med_dict_list
    
    def find(self, title = '', CAS = '', type_title = '', all = False):
        result_lis = []
        for each in self.lis:
            if title and title in each['title'] + each['aliasTitle'] + each['enTitle']:
                result_lis.append(each)
            elif CAS and CAS in each['CAS']:
                result_lis.append(each)
            elif type_title and type_title in each['type_title']:
                result_lis.append(each)
            if not all:
                if result_lis:
                    return result_lis
        if all:
            return result_lis
    
    def print(self, mode = ''):
        for each in self.lis:
            if mode == 'lab':
                print(each['title'], each['lave'] + each['dw'])
            if mode == 'title':
                print(each['title'])
            if mode == 'norm':
                print(each['title'], each['number'], each['norm'] + each['norm_unit_title'])

class Use(object):
    def __init__(self):
        self.lab_path = os.path.join('lab.txt')
        self.med_lis = []
        self.medicine_online = Medicine(url = 'https://seselab.tongji.edu.cn/api/admin-api/hxpIndex-yh', params = 'page=1&listRows=100')

    def load(self):
        with open('lab.txt', 'r', encoding = 'utf-8') as f:
            for line in f:
                if line:
                    tmp = line.split(' $ ')
                    local_CAS = tmp[2]
                    local_lave = tmp[3]
                    online_med = self.medicine_online.find(CAS = local_CAS)[0] # use_total
                    cpr = float(online_med['lave']) - float(local_lave)
                    dic = online_med.copy()
                    dic['use_total'] = cpr > 0 and cpr or 0
                    if dic['use_total']:
                        self.med_lis.append(dic)
    
    def add_use(self):
        self.load()
        url_get_med_num = 'https://seselab.tongji.edu.cn/api/admin-api/hxpkc-mx-yh' # 获取可用的药剂
        params_get_med_num = getDict('keys=7664-93-9&p_id=86&listRows=100', '&', '=')
        url_add = 'https://seselab.tongji.edu.cn/api/admin-api/hxpck-yh' # 添加使用记录
        data_add = getDict('p_id=86&uid[0]=1930570&uid[1]=1932819&time=2020-10-15 00:00&beizhu=&g_account=1932819&hxp[0][number]=177-00017529&hxp[0][chuwugui]=毒品柜（066-2）&hxp[0][used]=100&hxp[0][norm_unit]=567&hxp[0][norm_unit_title]=mL&hxp[0][wqr]=1&hxp[0][searchOptions]=&hxp[0][lave]=500&hxp[0][type]=556&hxp[0][h_id]=1302&hxp[0][norm]=500&hxp[0][lx]=1')
        for each in self.med_lis:
            params_get_med_num['keys'] = each['CAS']
            params_get_med_num['p_id'] = each['p_id']
            raw = getHTMLText(url_get_med_num, headers, params_get_med_num, cookies)
            med_num_lis = format_med(raw)
            need_use = each['use_total']
            med_num_lis.reverse()
            for bottle in med_num_lis:
                if float(bottle['lave']) > 0:
                    bottle['used'] = need_use > float(bottle['lave']) and bottle['lave'] or need_use
                    need_use -= float(bottle['used'])
                    time = strftime('%Y-%m-%d %H:%M:%S')[:-3] # 开始构造POST使用记录所需要的data
                    random_day = random.randint(1, int(time[8:10]))
                    for key in data_add.keys(): # 对已有数据批量填充
                        if 'hxp' in key:
                            sub_key = key.split('][')[1].strip('[]')
                            if sub_key in bottle.keys():
                                data_add[key] = bottle[sub_key]
                    data_add['time'] = time[:8] + str(random_day).rjust(2,'0') + time[-6:]
                    data_add['uid[0]'] = uid
                    data_add['uid[1]'] = uid2
                    data_add['g_account'] = uid2
                    data_add['hxp[0][chuwugui]'] = bottle['c_title'] + '（{}）'.format(bottle['cw_title'])
                    # print(data_add)
                    add = post_HTMLText(url_add, headers = headers, cookies = cookies, data = data_add)
                    if not need_use:
                        break
        
    def update(self):
        with open('lab.txt', 'w', encoding = 'utf-8') as f:
            for each in self.medicine_online.lis:
                if each['lave'] == '0' or each['type_title'] == '--':
                    continue
                tmp_str = (each['h_id'] + ' $ ' + each['title'] + ' $ ' + each['CAS']
                            + ' $ ' + each['lave'])
                f.write(tmp_str + '\n')
    
    def add_local(self, med_CAS):
        med = self.medicine_online.find(CAS = med_CAS)[0]
        with open('lab.txt', 'a', encoding = 'utf-8') as f:
            tmp_str = (med['h_id'] + ' $ ' + med['title'] + ' $ ' + med['CAS']
                        + ' $ ' + med['lave'])
            f.write(tmp_str + '\n')
    
    def confirm(self, switch = False):
        url_list = 'https://seselab.tongji.edu.cn/api/admin-api/hxpck-yh' # 读取待确认的列表
        params_list = getDict('status=1&page=1&listRows=100&uid=1930570')
        if not switch:
            params_list['uid'] = uid
        else:
            params_list['uid'] = uid2
        id_list = []
        old_text = ''
        page = 1
        while True:
            text = getHTMLText(url_list, headers, params_list, cookies)
            if '"data":[]' in text:
                break
            if text == old_text:
                break
            else:
                old_text = text
            project_list = format_med(text)
            for each in project_list:
                id_list.append(each['id'])
            page += 1
            params_list['page'] = page
        url_confirm = 'https://seselab.tongji.edu.cn/api/admin-api/setRr-yh' # 确认使用记录
        data_confirm = getDict('id=3060&_method=PUT')
        for id in id_list:
            data_confirm['id'] = id
            confirm = post_HTMLText(url_confirm, headers, cookies, data_confirm)

def load_account():
    global uid, uid2
    path_account = os.path.join('account.txt')
    if not os.path.exists(path_account):
        print('Account not exists!')
    else:
        with open(path_account, 'r') as f:
            raw = f.read()
        lis = raw.strip().split()
        uid = lis[0]
        uid2 = lis[2]

def main():
    global headers, cookies, medicine, cookies2
    h = '''
    accept: application/json, text/plain, */*
accept-encoding: gzip, deflate, br
accept-language: zh-CN,zh;q=0.9,en;q=0.8
authorization: eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1aWQiOiIxOTMyODE5IiwiZ3JvdXAiOjcsIm5hbWUiOiJcdTVmMjBcdTViNTBcdTgzOGUiLCJ2ZXJzaW9uIjowLCJpYXQiOjE2MTA0NTEyNDAsIm5iZiI6MTYxMDQ1MTI0MCwiZXhwIjoxNjEwNTM3NjQwfQ.kwZZn4Vo7MiGqis_CfCPfZfFYFMhX7Mwi347ByJbTkApKWQNu2_nXW02xf1J9AXFiCqMMARlr2P-1AAyntjt9wr_frnjueAe9kuo65RpGbxIPEz2qcHjXkM_C_bGkAOFmY4jfPrHwLscAobkx0ktMK4wHI8jECjM20Z468TwUsY
cache-control: no-cache
pragma: no-cache
referer: https://seselab.tongji.edu.cn/admin/usercenter/kucun
sec-fetch-dest: empty
sec-fetch-mode: cors
sec-fetch-site: same-origin
user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36
x-requested-with: XMLHttpRequest
'''
    c = 'PHPSESSID=qhcpg1565d552rt60aj4rlrdth'
    headers = get_headersDict(h)
    cookies = getDict(c, ';', '=')
    load_account()
    print('正在登录账号...')
    tongji_login = TongjiLogin()
    tongji_login.mode = 'baidu_ocr'
    phpsessid, auth = tongji_login.switch_account(0)
    headers['authorization'] = auth
    cookies['PHPSESSID'] = phpsessid
    medicine = Medicine(total = True)
    use = Use()
    use.update()
    input('请修改lab.txt')
    use.add_use()
    input('是否确认修改库存？')
    use.confirm()
    use.update()
    print('切换账号中...')
    phpsessid, auth = tongji_login.switch_account(1)
    headers['authorization'] = auth
    cookies['PHPSESSID'] = phpsessid
    use.confirm(switch = True)
    use.update()
    print('请确认修改后的库存')

if __name__ == '__main__':
    main()
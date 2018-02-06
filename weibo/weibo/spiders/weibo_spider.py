#! -*- encoding:utf-8 -*-
import re
import os
import time
import rsa,binascii
import base64
from urllib.parse import quote
from scrapy.spiders import CrawlSpider
from scrapy.http import Request
from scrapy.http import FormRequest
from scrapy.conf import settings


class WeiboSpider(CrawlSpider):
    '''
           scrapy模拟登录新浪微博
    '''
    name = 'weibo'
    user = settings['LOGIN_USER']
    password = settings['LOGIN_PWD']

    allowed_domains = ['weibo.com', 'sina.com.cn']
    start_urls = ['https://weibo.com/vanglis/profile?rightmod=1&wvr=6&mod=personinfo&ajaxpagelet=1&ajaxpagelet_v6=1&__ref=%2Fvanglis%2Fhome%3Fwvr%3D5%26lf%3Dreg&_t=FM_151755822351922']

    def start_requests(self):
        url = 'https://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=&rsakt=mod&client=ssologin.js(v1.4.19)&_=%s' % \
              (str(time.time()).replace('.', ''))
        print(url)
        return [Request(url=url, method='get', callback=self.post_message)]


    def post_message(self, response):
        '''
        提交登录数据，参数su为处理后的登录用户名，参数sp为处理后的密码，servertime，nonce，rsakv可以从上面的接口返回值拿到
        :param response:
        :return:
        '''
        regex = '{"retcode":0,"servertime":(.*),"pcid":"(.*)","nonce":"(.*)","pubkey":"(.*)","rsakv":"(.*)","exectime":(.*)}'
        serverdata = re.findall(regex, response.body.decode(encoding='utf-8'))
        servertime = serverdata[0][0]
        nonce = serverdata[0][2]
        pubkey = serverdata[0][3]
        rsakv = serverdata[0][4]
        print("servertime:{0}|nonce:{1}|pubkey:{2}|rsakv:{3}".format(servertime,nonce,pubkey,rsakv))
        su = base64.b64encode(quote(self.user).encode(encoding='utf-8')) #用户名先转义再base64编码处理得到su
        key = rsa.PublicKey(int(pubkey, 16), 65537)  #创建公钥
        message = ('\t').join([str(servertime), str(nonce)]) + '\n' + self.password
        message = message.encode(encoding='utf-8')
        encropy_pwd = rsa.encrypt(message, key)
        sp = binascii.b2a_hex(encropy_pwd)  # 将加密信息转换为16进制
        #print(sp)
        formdata = {"entry": 'weibo',
                    "gateway": '1',
                    "from": "",
                    "savestate": '7',
                    "qrcode_flag": 'false',
                    "useticket": '1',
                    "pagerefer": '',
                    "vsnf": '1',
                    "su": su,
                    "service": 'miniblog',
                    "servertime": servertime,
                    "nonce": nonce,
                    "pwencode": 'rsa2',
                    "rsakv": rsakv,
                    "sp": sp,
                    "sr": '1440*900',
                    "encoding": 'UTF-8',
                    "prelt": '506',
                    "url": 'https://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
                    "returntype": 'META'}

        return [FormRequest(url='http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)',
                            formdata=formdata, callback=self.set_cookie)]

    def set_cookie(self, response):
        '''
        拿到真正的登录地址，种下登录cookie
        '''
        new_login_url = re.search(r"location.replace\('(.*?)'\)", response.body.decode(encoding='utf-8')).group(1)
        request = Request(new_login_url)
        return request

    def parse(self, response):
        '''
        登录后的爬虫，parse方法会自动request遍历start_urls中的url
        '''

        for url in self.start_urls:
            request = Request(url=url, callback=self.parse_item)
            yield request

    def parse_item(self, response):
        '''
        处理items
        '''
        with open(os.path.join('./', 'logged.html'), 'wb') as html_file:
            html_page = response.body
            html_file.write(html_page)
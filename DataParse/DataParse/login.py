#!/usr/bin/env python
# coding:utf-8

from urllib import request, parse
import re


class UserLogin():
    """docstring for UserLogin"""

    def __init__(self):
        self.name = "cc0904wang@sina.com.cn"
        self.passwd = "wz09041020"
        self.headers = {
            "Host": "login.weibo.cn",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:38.0) Gecko/20100101\
             Firefox/38.0",
            "Accept": 'text/html,application/xhtml+xml,\
            application/xml;q=0.9,*/*;q=0.8',
            "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive"
        }

    def _post(self, url, data=None):
        if data is not None:
            if not isinstance(data, "bytes"):
                data = data.encode("utf-8")
        req = request.Request(url, data)
        try:
            resp = request.urlopen(req)
        except Exception as e:
            print("Exception:%e" % e)
        else:
            result = resp.read()
            return result.decode()
        finally:
            pass

    def getCaptchaInfo(self, loginUrl):
        html = self._post(loginUrl)
        return html


if __name__ == "__main__":
    ul = UserLogin()
    print(ul.getCaptchaInfo("http://www.weibob.com/login.php"))
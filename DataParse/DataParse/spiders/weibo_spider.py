#!/usr/bin/env python
# coding:utf-8

import scrapy
from DataParse.items import WeiboItem


class WeiboSpider(scrapy.Spider):
    """docstring for WeiboSpider"""

    name = "weibo"
    allowed_domains = ["weibo.com"]
    start_urls = [
        "http://weibo.com/login.php"
    ]

    def parse(self, response):
        item = WeiboItem()
        item["title"] = response.xpath("//title/text()").extract()
        item["content"] = response.xpath("//meta[4]/@content").extract()
        sel = response.xpath("//a")
        link_name = sel.xpath("text()").extract()
        link = sel.xpath("@href").extract()
        item["link"] = list(zip(link_name, link))
        return item

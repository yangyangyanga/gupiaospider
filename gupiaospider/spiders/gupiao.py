# -*- coding: utf-8 -*-
import scrapy
import time
import json
import os

class GupiaoSpider(scrapy.Spider):
    name = 'gupiao'
    start_urls = ['http://stock.10jqka.com.cn/']
    # 处理响应函数
    def parse(self, response):
        # print(response.text)
        a_list = response.xpath("//div[@id='rzrq']/table[@class='m-table']/tbody/tr/td[2]/a")
        # 获取股票简称和链接
        for text_href in a_list:
            text_name = text_href.xpath(".//text()").extract()[0]
            # print(text_name)
            href_url = text_href.xpath(".//@href").extract()[0]
            # print(href_url)
            time.sleep(3)
            yield scrapy.Request(href_url, callback=self.parse_data,
                                 meta={'text_name':text_name, "seindex":1})

    # 对每个股票的数据
    def parse_data(self, response):
        # print(response.meta["text_name"])
        # 想要获得的数据的页数
        seindex = response.meta["seindex"]
        # 获得每个股票的名称
        text_name = response.meta["text_name"]
        # 获得每条数据
        per_data = response.xpath("//table[@class='m-table']/tbody/tr/td/text()").extract()
        print(per_data)
        # 如果没有就退出
        if not per_data:
            return
        # 每一页50条数据
        data_split = []
        index = 0
        while index < len(per_data):
            temp = index + 11
            data_split.append(per_data[index:temp])
            index = temp
        # print(data_split)
        # 将每条数据存进一个字典里，然后添加进一个列表中
        datalist = []
        per_data_dict = {}
        for data in data_split:
            per_data_dict["序号"] = data[0]
            per_data_dict["交易时间"] = data[1].strip()
            per_data_dict["余额"] = data[2]
            per_data_dict["买入额"] = data[3]
            per_data_dict["偿还额"] = data[4]
            per_data_dict["融资净买入"] = data[5]
            per_data_dict["余量"] = data[6]
            per_data_dict["卖出量"] = data[7]
            per_data_dict["偿还量"] = data[8]
            per_data_dict["融券净卖出"] = data[9]
            per_data_dict["融资融券余额(元)"] = data[10]
            datalist.append(per_data_dict)
            per_data_dict = {}
        # 先将已存在的json文件读出来，再增加数据
        datad = []
        if os.path.isfile(text_name + ".json"):
            with open(text_name+".json", 'rb') as f:
                datad = json.load(f)
                # print(datad)
                # print(type(datad))
        datad.append(datalist)
        with open(text_name+".json", 'w', encoding='utf-8') as f:
            f.write(json.dumps(datad))
        # 每个股票的链接，根据它的链接获得各自的特定值
        print(response.url)
        if seindex != 1:
            spvalue = response.url.split("/")[-8]
        else:
            spvalue = response.url.split("/")[-2]
        print(spvalue)

        # ajax 加载的分页数据链接
        seindex += 1
        more_data_url =  "http://data.10jqka.com.cn/market/rzrqgg/code/"+str(spvalue)+"/order/desc/page/"+str(seindex)+"/ajax/1/"
        print("index = "+str(seindex))
        yield scrapy.Request(more_data_url, callback=self.parse_data,
                                 meta={"text_name":text_name, "seindex":seindex})


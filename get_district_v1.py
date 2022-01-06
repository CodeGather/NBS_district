#coding:utf-8
# 请求库
import requests
# 转拼音库
import pypinyin
import time
import datetime
# 用于导出表格
import csv
# 保存JSON文件
import json
import re
# 用于获取数组中随即代理
import random
# 解析html
from bs4 import BeautifulSoup

# 全部IP地址 '47.113.90.161:83', '47.100.255.35:80',
AllipData = ['49.233.173.151:9080', '121.5.145.187:8000', '222.64.95.60:9000', '47.100.14.22:9006']
YearData = []
# 从全部IP地址中过滤出可用的IP地址
UseAbleipData = []

# 国家统计局行政区划分首页
YearPage = "http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/"
# 请求头部参数
Headers = {
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
    'Accept-Encoding':'gzip, deflate',
    'Accept-Language':'zh-CN,zh;q=0.9',
    'Accept':'text/html,application/html,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Upgrade-Insecure-Requests':'1'
}

def getAllYearData():
    yearData = public_request(YearPage, True)
    if yearData.status_code == 404:
        print('国家统计局页面不存在，请检查页面后重试！')
    elif yearData.status_code == 500:
        print('国家统计局页面异常，请稍后重试！')
    else:
        html = yearData.text
        document = BeautifulSoup(html, "html.parser")
        a = document.select(".center_list_contlist > li > a")
        for aItem in a:
            yearItem = re.findall(r'\d{4}', aItem.get('href'))
            if yearItem is not None:
                YearData.append(yearItem[0])
        if len(YearData) > 0:
            getData()
        else:
            print("获取可用年份失败！")

def inspect_ip(ipprot):
     time.sleep(1)
     herder={
         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
         'Accept-Encoding':'gzip, deflate',
         'Accept-Language':'zh-CN,zh;q=0.9',
         'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
         'Upgrade-Insecure-Requests':'1'

     }

     url='https://www.baidu.com'
     proxies = { "http": "http://"+str(ipprot) }
     request=requests.get(url, headers=herder, proxies=proxies)
     if request.status_code==200:
         print('可用代理'+ipprot)
         AllipData.append(ipprot)
     else:
         print('不可用代理'+ipprot)

     randomData = random.sample(AllipData, 1)
     get_request(randomData[0])
     print('随机代理为：' + randomData[0])

def IPList_61():
    for q in [2]:
        url='http://www.66ip.cn/areaindex_'+str(q)+'/1.html'
        html = requests.get(url)
        html.encoding = html.apparent_encoding
        if html is not None:
            #print(html)
            iplistDocument=BeautifulSoup(html.text, "html.parser")
            iplist=iplistDocument.find_all('tr')
            # print(iplist)
            i=2
            for ip in iplist:
             if i<=0:
                 loader=''
                 # print(ip)
                 j=0
                 for ipport in ip.find_all('td', limit=2):
                     if j==0:
                        loader+=ipport.text.strip()+':'
                     else:
                        loader+=ipport.text.strip()
                     j=j+1
                 inspect_ip(loader)
             i=i-1
        time.sleep(1)

def get_request(ipprot):
    response = requests.get("http://api.taoshi168.com/api/test", proxies={"http": "http://" + str(ipprot)})
    print(response.text)


def get_ip_list():
    html = requests.get("http://api.89ip.cn/tqdl.html?api=1&num=20&port=&address=&isp=")
    html.encoding = html.apparent_encoding
    reg = re.compile(r'(\d+\.\d+\.\d+\.\d+:\d{1,5})')
    item = re.findall(reg, html.text)
    print(item)
    randomData = random.sample(item, 1)
    get_request(randomData[0])

def getData():
    str = input('请输入您要获取的年份\n')
    if str in YearData:
        print('开始处理', str, '的年国家统计局发布的行政区划分数据')
        # 待请求url
        url = 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/' + str + '/index.html'
        document = public_request(url)
        a = document.select(".provincetable a")

        proviceList = []
        for aItem in a:
            # if aItem.text == '海南省':
            get_provice(str, aItem, proviceList) # <a href="13.html">河北省<br/></a>

        print(proviceList)
        save_file(proviceList)
    else:
        print('您输入的不是数字，请输入符合的年份')
        getData()

# 保存文件
def save_file(jsonData):
    buffData = json.dumps(jsonData)
    fileName = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    file = open(fileName + '.json', 'w')
    file.write(buffData.encode('utf-8').decode("unicode-escape"))
    file.close()

def get_provice(yearItem, proviceItem, returnData):
    document = public_request(YearPage + yearItem + "/" +  proviceItem.get('href'))
    trList = document.select(".citytr") # <tr class="citytr"><td><a href="11/1101.html">110100000000</a></td><td><a href="11/1101.html">市辖区</a></td></tr>

    cityList = []
    # 开始循环城市信息
    for trItem in trList:
        # 处理城市的数据
        time.sleep(2)
        get_city(YearPage + yearItem + "/", trItem, proviceItem.get('href')[:-5], proviceItem.text, cityList)  # <a href="13.html">河北省<br/></a>

    # 添加到省份的数据当中
    returnData.append({
        'parentCode': '86',
        'parentName': '中国',
        'level': 1,
        'code': proviceItem.get('href')[:-5], # 省份code
        'name': proviceItem.text,
        'href': proviceItem.get('href'),
        'children': cityList
    })


def get_city(url, cityItem, parentCode, parentName, returnData):
    cityName = cityItem.contents[1].next_element.text
    cityCode = cityItem.contents[0].next_element.text
    cityHref = ""
    areaList = []
    if not isinstance(cityItem.contents[1].next_element, str):
        cityHref = cityItem.contents[1].next_element.get('href')
        document = public_request(url + cityItem.contents[1].next_element.get('href'))
        trList = document.select(".countytr")  # <tr class="countytr"><td><a href="01/110101.html">110101000000</a></td><td><a href="01/110101.html">东城区</a></td></tr>

        for trItem in trList:
            # 处理城市的数据
            get_area(url + parentCode + "/", trItem, cityCode, cityName, areaList)  # <a href="13.html">河北省<br/></a>

    # 添加到省份的数据当中
    returnData.append({
        'parentCode': parentCode, # 省份code
        'parentName': parentName,
        'level': 2,
        'code': cityCode,
        'name': cityName,
        'href': cityHref,
        'children': areaList
    })

def get_area(url, areaItem, parentCode, parentName, returnData):
    streetName = areaItem.contents[1].next_element.text
    streetCode = areaItem.contents[0].next_element.text
    streetHref = ""
    streetList = []

    if not isinstance(areaItem.contents[1].next_element, str):
        streetHref = areaItem.contents[1].next_element.get('href')

        document = public_request(url + areaItem.contents[1].next_element.get('href'))
        trList = document.select(".towntr")  # <tr class="towntr"><td><a href="01/110101001.html">110101001000</a></td><td><a href="01/110101001.html">东华门街道</a></td></tr>

        for trItem in trList:
            # 处理城市的数据
            committeeData = get_committee(url + streetHref[0:streetHref.index('/')] + "/", trItem, trItem.contents[0].next_element.text, trItem.contents[1].next_element.text, [])  # <a href="13.html">河北省<br/></a>
            streetList.append({
                'parentCode': streetCode,  # 街道code
                'parentName': streetName,
                'level': 4,
                'code': trItem.contents[0].next_element.text,
                'name': trItem.contents[1].next_element.text,
                'href': trItem.contents[1].next_element.get('href'),
                'children': committeeData
            })

    # 添加到省份的数据当中
    returnData.append({
        'parentCode': parentCode,  # 城市code
        'parentName': parentName,
        'level': 3,
        'code': streetCode, # 街道code
        'name': streetName,
        'href': streetHref,
        'children': streetList
    })

def get_committee(url, areaItem, parentCode, parentName, returnData):
    if not isinstance(areaItem.contents[1].next_element, str):
        document = public_request(url + areaItem.contents[1].next_element.get('href'))
        trList = document.select(".villagetr")  # <tr class="villagetr"><td>110101001001</td><td>111</td><td>多福巷社区居委会</td></tr>
        for trItem in trList:
            # 处理城市的数据
            returnData.append({
                'parentCode': parentCode,  # 城市code
                'parentName': parentName,
                'level': 5,
                'code': trItem.contents[0].text,
                'name': trItem.contents[2].text,
                'href': "",
                'children': []
            })

    print(returnData)
    return returnData

def public_request(url, type=False):
    # randomData = random.sample(AllipData, 1)
    # print("IP地址：" + randomData[0])
    print("请求链接：" + url)
    requests.adapters.DEFAULT_RETRIES = 5  # 增加重连次数
    newRequests = requests.session()
    newRequests.keep_alive = False  # 关闭多余连接
    # requestData = newRequests.request("get", url, headers=Headers, proxies={"http": "http://" + randomData[0]})
    requestData = newRequests.request("get", url, headers=Headers)
    requestData.encoding = requestData.apparent_encoding
    if type:
        return requestData
    else:
        html = requestData.text
        document = BeautifulSoup(html, "html.parser")
        return document

if __name__ == '__main__':
    # print('1,2,3,4'[0:'0,1,2,3,4'.index(',')])
    getAllYearData()
    # IPList_61()
    # get_ip_list()
    # get_request('47.100.14.22:9006')
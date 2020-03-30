'''
爬取的url：主页："https://www.shixiseng.com/interns?page=1&keyword=python&type=intern&area=%E9%BB%84%E6%B5%A6%E5%8C%BA&salary=-0&city=%E4%B8%8A%E6%B5%B7"
                "https://www.shixiseng.com/interns?page=3&keyword=python&type=intern&salary=-0&city=%E4%B8%8A%E6%B5%B7&"
    json链接："https://www.shixiseng.com/app/interns/search/v2?build_time=1581229670576&page=1&keyword=python&type=intern&salary=-0&city=%E4%B8%8A%E6%B5%B7"
        详情页：
爬取的内容：主页：地区，详情页url
        详情页：标题 ，发布时间，佣金， 地方 ， 学历，职位描述， 投递要求
导入的依赖：requests beautiful,time,re
'''

import requests,time,json,re,threading
from bs4 import BeautifulSoup

headers = {
    "user-agent":"Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"
}

#获取网页源码
def get_html(url):
    '''
    接收url，通过requests获取网页源码，并用beautiful进行解析后返回解析后的网页源码
    :param url: 访问网页的url
    :return: 解析后的html源码
    '''
    req = requests.get(url,headers = headers)
    soup = BeautifulSoup(req.text,"lxml")
    return soup

#获取地区主页的每个工作的url
def get_page(html):
    '''
    通过接收解析后的html，返回页面
    :param html: 解析后的地区html
    :return: 返回页面
    '''
    page = html.select(".number")[-1].text
    return int(page)


#解析json文件
def get_json(url):
    '''
    根据传入的html解析获得详情页的url
    :param html: json
    :return: 详情页的url
    '''
    req = requests.get(url)
    js = json.loads(req.text)["msg"]["data"]
    js_url = ["https://www.shixiseng.com/intern/{}".format(i["uuid"]) for i in js]
    # print(js_url)
    return js_url

#转换字体
def change_font(strs):
    a = strs
    a = a.replace(b"\xef\x84\x9e", b"0")
    a = a.replace(b"\xef\x8d\x96", b"1")
    a = a.replace(b"\xef\x84\x8d", b"2")
    a = a.replace(b"\xef\xa1\x9e", b"3")
    a = a.replace(b"\xee\xbc\xab", b"4")
    a = a.replace(b"\xee\xb1\x90", b"5")
    a = a.replace(b"\xee\xad\xa3", b"6")
    a = a.replace(b"\xee\x92\xb5", b"7")
    a = a.replace(b"\xee\x96\xbd", b"8")
    a = a.replace(b"\xef\x9b\xb9", b"9")
    return a.decode("utf-8")


#解析详情页获得标题 ，发布时间，佣金， 地方 ， 学历，职位描述， 投递要求并写入文件
def get_details(html):
    '''
    解析详情页获得标题 ，发布时间，佣金， 地方 ， 学历，职位描述， 投递要求并写入文件
    :param html: 需要解析的html
    :return: None
    '''
    title = html.select(".new_job_name")[0].text
    txt = open(r".\text\{}.txt".format(title.replace("\n","")),"w+",encoding="utf-8")
    release_time = html.select(".job_date span")[0].text
    release_time = change_font(release_time.encode("utf-8"))
    money = html.select(".job_money.cutom_font")[0].text
    money = change_font(money.encode("utf-8"))
    place = html.select(".job_position")[-1]["title"]
    xueli = html.select(".job_academic")[-1].text.strip()
    shixiyaoqiu = html.select(".job_week.cutom_font")[0].text.strip()
    shixiyaoqiu = change_font(shixiyaoqiu.encode("utf-8"))
    shixizhouchang = html.select(".job_time.cutom_font")[0].text.strip()
    shixizhouchang = change_font(shixizhouchang.encode("utf-8"))
    zhiweimiaoshu = html.select(".job_detail")[0].text.replace("\n","").replace("   ","")
    txt.write(title)
    txt.write("\n")
    txt.write(release_time)
    txt.write("\n")
    txt.write(money)
    txt.write(" ")
    txt.write(place)
    txt.write(" ")
    txt.write(xueli)
    txt.write(" ")
    txt.write(shixiyaoqiu)
    txt.write(" ")
    txt.write(shixizhouchang)
    txt.write("\n")
    str2 = zhiweimiaoshu.split("；")
    for i in str2:
        if "职位描述" in i or "任职要求" in i:
            i = i.replace("：", "\n")
        txt.write(i.strip())
        txt.write("\n")
    txt.write("\n\n以下为投递要求：\n\n")
    toudiyaoqiu = html.select(".con-job")[1]
    toudiyaoqiu = [str(i) for i in toudiyaoqiu]
    str2 = [toudiyaoqiu[i] for i in range(len(toudiyaoqiu)) if i % 2 != 0]
    com = re.compile("<div.*?>(.*?)</div>")
    str3 = [com.findall(i) for i in str2]
    for s in str3[1:]:
        s = change_font(s[0].encode("utf-8"))
        txt.write(s)
        txt.write("\n")
    # print(toudiyaoqiu)
    # assert False

#main程序接口，构造翻页的url
def main():
    url = "https://www.shixiseng.com/interns?page=1&keyword=python&type=intern&area=%E9%BB%84%E6%B5%A6%E5%8C%BA&salary=-0&city=%E4%B8%8A%E6%B5%B7"
    html = get_html(url)
    page = get_page(html)
    json_url = ["https://www.shixiseng.com/app/interns/search/v2?build_time={}&page={}&keyword=python&type=intern&salary=-0&city=%E4%B8%8A%E6%B5%B7".format(time.time(), i) for i in range(1,page + 1)]
    for j in json_url:
        detail_url = get_json(j)
        for d in detail_url:
            detail_html = get_html(d)
            g = threading.Thread(target=get_details,args=(detail_html,))
            g.start()
            # get_details(detail_html)

if __name__ == '__main__':
    print("正在爬取，请稍后")
    main()
    while True:
        if threading.activeCount() == 1:
            print("爬取已完成")
            exit()
    # a = None
    # change_font(a)



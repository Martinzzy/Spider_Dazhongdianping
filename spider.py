import requests
import time
import pymongo
from pyquery import PyQuery as pq
from requests.exceptions import ConnectionError

client = pymongo.MongoClient('localhost')
db = client['DZDP']
proxy = None
headers = {
            'Host': 'www.dianping.com',
            'Referer': 'http://www.dianping.com/nanjing/food',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3377.1 Safari/537.36'}

def get_proxy():
    try:
        res = requests.get('http://127.0.0.1:5555/random')
        if res.status_code == 200:
            proxy = res.text
            return proxy
        return None
    except ConnectionError:
        print('获取代理失败')

def get_one_page(url):
    global proxy
    try:
        if proxy:
            proxies = {'http':'http://'+proxy}
            res = requests.get(url,headers=headers,proxies=proxies)
        else:
            res = requests.get(url,headers=headers)
            print(res.status_code)
        if res.status_code == 200:
            html = res.text
            return html
        if res.status_code == 403:
            proxy = get_proxy()
            if proxy:
                print('正在使用代理:',proxy)
                return get_one_page(url)
            else:
                print('获取代理失败')
                return None
    except ConnectionError:
        print('请求初始页失败')
        proxy = get_proxy()
        return get_one_page(url)

def parse_one_page(url,html):
    try:
        doc = pq(html)
        items = doc('#shop-all-list ul li').items()
        for item in items:
            title = item.find('.tit a h4').text()
            tag = item.find('.tag-addr a').text()
            location = item.find('.tag-addr .addr').text()
            stars = item.find('.comment span').attr['title']
            review_num = item.find('.comment .review-num').text()
            mean_price = item.find('.comment .mean-price').text()
            comment = item.find('.txt .comment-list').text()
            recommand_food = item.find('.txt .recommend').text()
            svr_info = item.find('.svr-info a').text()
            data = {'title':title,
                    'tag':tag,
                    'location':location,
                    'stars':stars,
                    'review_num':review_num,
                    'mean_price':mean_price,
                   'comment':comment,
                    'recommand_food':recommand_food,
                    'svr_info':svr_info
                    }
            save_to_mongo(data)
    except TypeError:
        print('解析网页失败')
        proxy = get_proxy()
        return get_one_page(url)

def save_to_mongo(data):
    if data and db['huoguo'].insert(data):
        print('存储到MongoDB数据库成功',data)
    else:
        print('存储到MongoDB数据库失败',data)

def main():
    keyword = input('请输入你要搜索的内容:')
    # keyword = '火锅'
    for page in range(1,50):
        url = 'http://www.dianping.com/search/keyword/5/10_{}/p{}'.format(keyword,page)
        print('正在爬取第{}页'.format(page))
        html = get_one_page(url)
        parse_one_page(url,html)
        time.sleep(2)
if __name__ == '__main__':
    main()

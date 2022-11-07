import re
import time
from bs4 import BeautifulSoup
from numpy import random
import requests
from pykrx import stock

from dataManage import db

headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.79 Safari/537.36"}

def clearData(ref):
    docs = ref.stream()
    for doc in docs:
        doc.reference.delete()

def seenNewsCrawler():
    webpage = requests.get('https://finance.naver.com/news/news_list.naver?mode=RANK').text
    soup = BeautifulSoup(webpage, 'html.parser')
    newss = soup.find('ul', attrs={"class": "simpleNewsList"})
    result = []
    for index in range(0, 5):
        value = {}
        title = newss.select('a')[index]['title']
        url = newss.select('a')[index]['href']
        value['title'] = title
        value['url'] = f'https://finance.naver.com{url}'
        imgpage = requests.get(f'https://finance.naver.com{url}', headers=headers).text
        imgsoup = BeautifulSoup(imgpage, 'html.parser')
        imgSpan = imgsoup.find('span', attrs={"class": "end_photo_org"})
        imgUrl = imgSpan.select('img')[0]['src']
        value['img'] = imgUrl
    newsRefs = db.collection('news')
    clearData(newsRefs)
    for data in result:
        doc_ref = newsRefs.document(data['title'])
        doc_ref.set({
            'title': data['title'],
            'url': data['url'],
            'img': data['img']
        })



def newsCrawler(ticker):
    webpage = requests.get(f'https://finance.naver.com/item/news_news.naver?code={ticker}&page=1').text
    soup = BeautifulSoup(webpage, 'html.parser')
    results = []
    titles = soup.select('.title')
    links = soup.select('.title')
    dates = soup.select('.date')
    sources = soup.select('.info')

    for index in range(0, 4):
        map = {}
        title = titles[index].get_text()
        title = re.sub('\n', '', title)
        map['title'] = title

        link_url = 'https://finance.naver.com' + links[index].find('a')['href']
        map['link'] = link_url

        map['date'] = dates[index].get_text()

        map['source'] = sources[index].get_text()

        results.append(map)
    time.sleep(3)
    return results


def noticeCrawler(ticker):
    webpage = requests.get(f'https://finance.naver.com/item/news_notice.naver?code={ticker}&page=1').text
    soup = BeautifulSoup(webpage, 'html.parser')
    results = []
    titles = soup.select('.title')
    links = soup.select('.title')
    dates = soup.select('.date')
    sources = soup.select('.info')

    for index in range(0, 4):
        result = {}
        title = titles[index].get_text()
        title = re.sub('\n', '', title)
        result['title'] = title

        link_url = 'https://finance.naver.com' + links[index].find('a')['href']
        result['link'] = link_url

        result['date'] = dates[index].get_text()
        result['source'] = sources[index].get_text()
        results.append(result)
    time.sleep(2)
    return results


def saveNews(ticker):
    newsRefs = db.collection('stocks').document(ticker).collection('news')
    clearData(ticker, newsRefs)
    news = newsCrawler(ticker)
    rand_value = random.randint(1, 7)
    time.sleep(rand_value)
    for data in news:
        doc_ref = newsRefs.document(data['title'])
        doc_ref.set({
            'title': data['title'],
            'date': data['date'],
            'link': data['link'],
            'source': data['source']
        })


def saveNotice(ticker):
    noticeRefs = db.collection('stocks').document(ticker).collection('notice')
    clearData(ticker, noticeRefs)
    rand_value = random.randint(1, 7)
    time.sleep(rand_value)
    notice = noticeCrawler(ticker)
    for data in notice:
        doc_ref = noticeRefs.document(data['title'])
        doc_ref.set({
            'title': data['title'],
            'date': data['date'],
            'link': data['link'],
            'source': data['source']
        })


if __name__ == "__main__":
    print(newsCrawler('000660'))

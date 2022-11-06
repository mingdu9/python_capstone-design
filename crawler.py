import re
import time
from bs4 import BeautifulSoup
from numpy import random
import requests
from pykrx import stock

from dataManage import db


def clearData(ticker, ref):
    docs = ref.stream()
    for doc in docs:
        doc.reference.delete()


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
    for ticker in stock.get_index_portfolio_deposit_file('1035'):
        if stock.get_index_portfolio_deposit_file('1894').__contains__(ticker):
            continue
        else:
            saveNews(ticker)
            time.sleep(3)
            saveNotice(ticker)
            time.sleep(3)
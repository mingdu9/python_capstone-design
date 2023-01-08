import re
import time
from bs4 import BeautifulSoup
from numpy import random
import requests
from pykrx import stock

from dataManage import db

# 타겟 웹페이지가 서버의 IP를 차단하지 않도록 우회하는 헤더
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.79 Safari/537.36"}


# ref에 담긴 문서들을 전부 삭제
def clearData(ref):
    docs = ref.stream()
    for doc in docs:
        doc.reference.delete()


# 많이 본 뉴스 스크래핑
def seenNewsScrapper():
    # 웹 페이지 HTTP GET 요청하여 텍스트 형태로 수신
    webpage = requests.get('https://finance.naver.com/news/news_list.naver?mode=RANK', headers=headers).text
    # 받은 HTML 텍스트를 파서로 파싱
    soup = BeautifulSoup(webpage, 'html.parser')
    # 필요한 데이터 찾기
    seenNews = soup.find('ul', attrs={"class": "simpleNewsList"})
    result = []
    for index in range(0, 5):  # 최상위 5개만 저장
        value = {}
        title = seenNews.select('a')[index]['title']
        url = seenNews.select('a')[index]['href']
        value['title'] = title
        value['url'] = f'https://finance.naver.com{url}'
        # 이미지 주소 추출
        imgpage = requests.get(f'https://finance.naver.com{url}', headers=headers).text
        imgsoup = BeautifulSoup(imgpage, 'html.parser')
        imgSpan = imgsoup.find('span', attrs={"class": "end_photo_org"})
        imgUrl = imgSpan.select('img')[0]['src']
        value['img'] = imgUrl
        result.append(value)
    # 데이터베이스에 저장
    for data in result:
        doc_ref = db.collection('news').document(data['title'])
        doc_ref.set({
            'title': data['title'],
            'url': data['url'],
            'img': data['img']
        })


def newsScrapper(ticker):
    # 웹 페이지 로딩
    webpage = requests.get(f'https://finance.naver.com/item/news_news.naver?code={ticker}&page=1', headers=headers).text
    # HTML 파싱
    soup = BeautifulSoup(webpage, 'html.parser')
    results = []
    # 필요한 데이터 찾기
    titles = soup.select('.title')
    links = soup.select('.title')
    dates = soup.select('.date')
    sources = soup.select('.info')
    print(titles.__class__);

    # 애플리케이션에 필요한 최소 3개 최대 4개의 데이터 가공
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
    # 웹 페이지에의 부담을 덜기 위한 지연시간
    time.sleep(2)
    return results


def noticeScrapper(ticker):
    # 웹 페이지 로딩
    webpage = requests.get(f'https://finance.naver.com/item/news_notice.naver?code={ticker}&page=1', headers=headers).text
    # HTML 파싱
    soup = BeautifulSoup(webpage, 'html.parser')
    results = []
    # 필요한 데이터 찾기
    titles = soup.select('.title')
    links = soup.select('.title')
    dates = soup.select('.date')
    sources = soup.select('.info')

    # 애플리케이션에 필요한 최소 3개 최대 4개의 데이터 가공
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
    # 웹 페이지에의 부담을 덜기 위한 지연시간
    time.sleep(2)
    return results


# 추출된 데이터들을 데이터베이스에 저장
def saveNews(ticker):
    newsRefs = db.collection('stocks').document(ticker).collection('news')
    # 원래 문서에 있던 문서들 삭제
    clearData(newsRefs)
    # 티커의 관련 뉴스 반환
    news = newsScrapper(ticker)
    for data in news:
        doc_ref = newsRefs.document(data['title'])
        doc_ref.set({
            'title': data['title'],
            'date': data['date'],
            'link': data['link'],
            'source': data['source']
        })


# 추출된 데이터들을 데이터베이스에 저장
def saveNotice(ticker):
    noticeRefs = db.collection('stocks').document(ticker).collection('notice')
    # 원래 문서에 있던 문서들 삭제
    clearData(noticeRefs)
    # 티커의 공시 정보 반환
    notice = noticeScrapper(ticker)
    for data in notice:
        doc_ref = noticeRefs.document(data['title'])
        doc_ref.set({
            'title': data['title'],
            'date': data['date'],
            'link': data['link'],
            'source': data['source']
        })


if __name__ == "__main__":
    newsScrapper('005930')

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, jsonify
from pytz import timezone

import os
from dataManage import get_data
from scrapper import saveNews, saveNotice, seenNewsScrapper
from readWIKI import getTerm, getNewTerm

KST = timezone('Asia/Seoul')
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False


# 많이 본 뉴스 스크래핑
@app.route('/seen')
def updateSeenNews():
    seenNewsScrapper()
    return 'ok'


# 해당 인덱스의 시사 경제 용어 스크래핑
@app.route('/term/<index>')
def sendTerm(index):
    return jsonify(getTerm(index))


# 랜덤한 인덱스의 시사 경제 용어 스크래핑
@app.route('/term')
def makeNewTerm():
    return jsonify(getNewTerm())


# 해당 티커의 종목 관련 뉴스 스크래핑
@app.route('/news/<ticker>')
def getNews(ticker):
    saveNews(ticker)
    return 'ok'


# 해당 티커의 공시 정보 스크래핑
@app.route('/notice/<ticker>')
def getNotice(ticker):
    saveNotice(ticker)
    return 'ok'


# 영업일 16시마다 주식 종가 데이터 스크래핑 및 크롤링
scheduler = BackgroundScheduler(daemon=True, timezone=KST)
scheduler.start()
scheduler.add_job(get_data, 'cron', day_of_week='0-4', hour='16', minute='00')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

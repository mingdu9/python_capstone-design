from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, jsonify
from pytz import timezone

import os
from dataManage import get_data
from crawler import saveNews, saveNotice
from readWIKI import getTerm, getNewTerm

KST = timezone('Asia/Seoul')
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False


@app.route('/term/<index>')
def sendTerm(index):
    return jsonify(getTerm(index))


@app.route('/term')
def makeNewTerm():
    return jsonify(getNewTerm())


@app.route('/news/<ticker>')
def getNews(ticker):
    saveNews(ticker)
    return 'ok'


@app.route('/notice/<ticker>')
def getNotice(ticker):
    saveNotice(ticker)
    return 'ok'


scheduler = BackgroundScheduler(daemon=True, timezone=KST)
scheduler.start()
scheduler.add_job(get_data, 'cron', day_of_week='0-4', hour='00', minute='00')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

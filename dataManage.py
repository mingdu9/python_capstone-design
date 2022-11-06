from pykrx import stock
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
import time
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate('capstone-63854-firebase-adminsdk-7brrs-bc7dfa22a7.json')
firebase_admin.initialize_app(cred, {
    'projectId': 'capstone-63854',
})

db = firestore.client()
batch = db.batch()
current_time = datetime.now()


def get_ticker_info(ticker):
    name = stock.get_market_ticker_name(ticker)
    day_ago = current_time - relativedelta(days=1)
    refs = db.collection('stocks')
    query1 = refs.document(ticker).collection('data').where('date', '==', day_ago.strftime('%Y-%m-%d')).get()
    volume = 0
    for data in query1:
        volume = data.to_dict()['volume']
    query = refs.document('indexes').collection('category').where('portfolio', 'array_contains', ticker).get()
    index_list = []
    for data in query:
        index = data.to_dict()['name']
        index_list.append(index)
    doc_ref = refs.document(ticker)
    doc_ref.set({
        'ticker': ticker,
        'name': name,
        'index': index_list,
        'volume': volume
    })


def get_index_info():
    for ticker in stock.get_index_ticker_list():
        refs = db.collection('stocks').document('indexes').collection('category').document(ticker)
        refs.set({
            'ticker': ticker,
            'name': stock.get_index_ticker_name(ticker),
            'portfolio': stock.get_index_portfolio_deposit_file(ticker)
        })
        time.sleep(1)


def get_data_day(ticker):
    refs = db.collection('stocks').document(ticker).collection('data')
    month_ago = current_time - relativedelta(months=1)
    df = stock.get_market_ohlcv(month_ago.strftime('%Y%m%d'), current_time.strftime('%Y%m%d'), ticker, adjusted=False)
    df = df.reset_index()
    samples = pd.DataFrame({
        'date': df.날짜,
        'closingPrice': df.종가,
        'volume': df.거래량,
        'fluctuation': df.등락률
    })
    samples = samples.astype({"date": "string",
                              "closingPrice": "int64",
                              "volume": "int64",
                              })
    a = samples.loc[len(samples) - 1].to_dict()
    db.collection('stocks').document(ticker).update(
        {'volume': a['volume'], }
    )
    for num in range(0, len(samples)):
        dayData = samples.loc[num].to_dict()
        doc_ref = refs.document(dayData['date'])
        dayData['fluctuation'] = round(dayData['fluctuation'], 2)
        doc_ref.set({
            'date': dayData['date'],
            'closingPrice': dayData['closingPrice'],
            'volume': dayData['volume'],
            'fluctuation': dayData['fluctuation']
        })



def set_month(ticker):
    refs = db.collection('stocks').document(ticker).collection('data')
    datas = refs.get()
    month = 30
    if len(datas) > month:
        size = len(datas) - month
        for n in range(0, size):
            datas[n].reference.delete()


def get_data():
    print("get_data")
    for ticker in stock.get_index_portfolio_deposit_file('1035'):
        print(ticker)
        get_data_day(ticker)
        time.sleep(2)


if __name__ == "__main__":
    get_data()

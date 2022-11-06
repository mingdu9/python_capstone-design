import pandas as pd
from numpy import random



def getTerm(index):
    df = pd.read_excel('시사경제용어사전.xls')
    df.dropna()
    result = df[df['순번'] == index].reset_index()
    result = result.loc[0].to_dict()
    term = {
        'index': result['순번'],
        'topic': result['주제'],
        'term': result['용어'],
        'ex': result['설명']
    }
    return term


def getNewTerm():
    df = pd.read_excel('시사경제용어사전.xls')
    df.dropna()
    rand_value = random.randint(1, 3031)
    result = df[df['순번'] == rand_value].reset_index()
    result = result.loc[0].to_dict()
    term = {
        'index': result['순번'],
        'topic': result['주제'],
        'term': result['용어'],
        'ex': result['설명']
    }
    return term


if __name__ == "__main__":
    print(getNewTerm())

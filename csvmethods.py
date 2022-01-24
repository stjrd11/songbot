import pandas as pd
from datetime import datetime
import random

def createBackup():
    df1 = pd.read_csv('data.csv')
    df1.to_csv('dataBackup.csv', index=False)
    df2 = pd.read_csv('bannedSongs.csv')
    df2.to_csv('bannedSongsBackup.csv', index=False)
    df3 = pd.read_csv('savedSongs.csv')
    df3.to_csv('savedSongsBackup.csv', index=False)

def addUser(user):
    df = pd.DataFrame({'username':[user],
                        'prioBump': [0],
                        'bump': [0],
                        'bumpLimit': [0],
                        'playedLimit': [0],
                        'extend': [0],
                        'raffleWins': [0],
                        'joinEligible': [0]})
    df.to_csv('data.csv', mode='a', index=False, header=False)

def getUserExtended(user):
    df = pd.read_csv('data.csv')
    userCheck = user in df.values
    if userCheck is False:
        addUser(user)
    df = pd.read_csv('data.csv')
    for i in range(len(df.username)):
        if user == df.username[i]:
            return df.extend[i]

def addUserExtended(user):
    newValue = getUserExtended(user) + 1
    df = pd.read_csv('data.csv')
    for i in range(len(df.username)):
        if user == df.username[i]:
            df.at[i, 'extend'] = newValue
            df.to_csv('data.csv', index=False)

def useExtend(user):
    newValue = getUserExtended(user) - 1
    df = pd.read_csv('data.csv')
    for i in range(len(df.username)):
        if user == df.username[i]:
            df.at[i, 'extend'] = newValue
            df.to_csv('data.csv', index=False)

def findUser(user):
    df = pd.read_csv('data.csv')
    userCheck = user in df.values
    if userCheck is False:
        return False
    else:
        return True

def banCheck(url):
    df = pd.read_csv('bannedSongs.csv')
    for i in range(len(df.link)):
        if url == df.link[i]:
            return True
        else:
            return False

def getDate(seconds):
    seconds = int(seconds)
    date_time = datetime.fromtimestamp(seconds)
    date = date_time.strftime("%b %d, %Y")
    return date

def checkRaffle(user):
    df = pd.read_csv('raffleList.csv')
    for i in range(len(df.username)):
        if user == df.username[i]:
            return 1
        else:
            return 0

def checkWinner(user):
    df = pd.read_csv('data.csv')
    for i in range(len(df.username)):
        if user == df.username[i]:
            if df.joinEligible[i] == 0:
                return 0
            else:
                return 1

def addToRaffle(user):
    df = pd.DataFrame({'username':[user]})
    df.to_csv('raffleList.csv', mode='a', index=False, header=False)

def getWinner():
    df = pd.read_csv('raffleList.csv')
    rows = len(df.axes[0])
    if rows == 0:
        return 0
    elif rows == 1:
        return df.username[1]
    else:
        rows = rows - 1
        randomNum = random.randint(0, rows - 1)
        user = df.username[randomNum]
        return user

def addRaffleWin(user):
    df = pd.read_csv('data.csv')
    for i in range(len(df.username)):
        if user == df.username[i]:
            number = df.at[i, 'raffleWins']
            number = number + 1
            df.at[i, 'raffleWins'] = number
            df.at[i, 'joinEligible'] = 1
    df.to_csv('data.csv', index=False)

def resetEligible():
    df = pd.read_csv('data.csv')
    for i in range(len(df.username)):
        df.at[i, 'joinEligible'] = 0
    df.to_csv('data.csv', index=False)

def resetRaffle():
    df = pd.read_csv('raffleList.csv')
    for i in range(len(df.username)):
        df.drop(i, axis=0, inplace=True)
    df.to_csv('raffleList.csv', index=False)
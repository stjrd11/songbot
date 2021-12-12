import pandas as pd
from botconfig import *
import csvmethods as csvm

def getUserBump(user):
    df = pd.read_csv('data.csv')
    userCheck = user in df.values
    if userCheck is False:
        csvm.addUser(user)
    df = pd.read_csv('data.csv')
    for i in range(len(df.username)):
        if user == df.username[i]:
            return df.bump[i]

def getUserPrio(user):
    df = pd.read_csv('data.csv')
    userCheck = user in df.values
    if userCheck is False:
        csvm.addUser(user)
    df = pd.read_csv('data.csv')
    for i in range(len(df.username)):
        if user == df.username[i]:
            return df.prioBump[i]

def getUserLimit(user):
    df = pd.read_csv('data.csv')
    userCheck = user in df.values
    if userCheck is False:
        csvm.addUser(user)
    df = pd.read_csv('data.csv')
    for i in range(len(df.username)):
        if user == df.username[i]:
            return df.bumpLimit[i]

def getBumpsPlayedLimit(user):
    df = pd.read_csv('data.csv')
    userCheck = user in df.values
    if userCheck is False:
        csvm.addUser(user)
    df = pd.read_csv('data.csv')
    for i in range(len(df.username)):
        if user == df.username[i]:
            return df.playedLimit[i]

def addUserBump(user):
    bump = getUserBump(user)
    if bump >= maxStoredBumps:
        pass
    else:
        newValue = bump + 1
        df = pd.read_csv('data.csv')
        for i in range(len(df.username)):
            if user == df.username[i]:
                df.at[i, 'bump'] = newValue
                df.to_csv('data.csv', index=False)

def addUserPrio(user):
    prioBump = getUserPrio(user)
    if prioBump >= maxStoredPrio:
        pass
    else:
        newValue = getUserPrio(user) + 1
        df = pd.read_csv('data.csv')
        for i in range(len(df.username)):
            if user == df.username[i]:
                df.at[i, 'prioBump'] = newValue
                df.to_csv('data.csv', index=False)

def addUserLimit(user):
    newValue = getUserLimit(user) + 1
    df = pd.read_csv('data.csv')
    for i in range(len(df.username)):
        if user == df.username[i]:
            df.at[i, 'bumpLimit'] = newValue
            df.to_csv('data.csv', index=False)

def addBumpsPlayedLimit(user):
    newValue = getBumpsPlayedLimit(user) + 1
    df = pd.read_csv('data.csv')
    for i in range(len(df.username)):
        if user == df.username[i]:
            df.at[i, 'playedLimit'] = newValue
            df.to_csv('data.csv', index=False)

def useBump(user):
    newValue = 0
    df = pd.read_csv('data.csv')
    for i in range(len(df.username)):
        if user == df.username[i]:
            df.at[i, 'bump'] = newValue
            df.to_csv('data.csv', index=False)

def usePrio(user):
    newValue = 0
    df = pd.read_csv('data.csv')
    for i in range(len(df.username)):
        if user == df.username[i]:
            df.at[i, 'prioBump'] = newValue
            df.to_csv('data.csv', index=False)

def resetLimit():
    df = pd.read_csv('data.csv')
    for i in range(len(df.bumpLimit)):
        df.at[i, 'bumpLimit'] = 0
        df.at[i, 'playedLimit'] = 0
        df.at[i, 'prioBump'] = 0
    df.to_csv('data.csv', index=False)

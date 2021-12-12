import pandas as pd

def createBackup():
    df = pd.read_csv('data.csv')
    df.to_csv('dataBackup.csv', index=False)

def addUser(user):
    df = pd.DataFrame({'username':[user],
                        'prioBump': [0],
                        'bump': [0],
                        'bumpLimit': [0],
                        'playedLimit': [0],
                        'extend': [0]})
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
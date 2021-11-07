import os

def getUserBump(user):
    file_name = os.path.exists(f"bumps/{user}bump.txt")
    if file_name == False:
        bump = 0
        bumpStr = str(bump)
        file = open(f"bumps/{user}bump.txt", "a+")
        file.write(bumpStr)
        file.close()
    file = open(f"bumps/{user}bump.txt", "r")
    userBump = file.readlines()
    file.close()
    userBumpInt = int(userBump[0])
    return userBumpInt

def addUserBump(user):
    userBump = getUserBump(user) + 1
    file = open(f"bumps/{user}bump.txt", "w")
    userBumpStr = str(userBump)
    file.write(userBumpStr)
    file.close()
    addUserLimit(user)

def getUserLimit(user):
    file_name = os.path.exists(f"bumplimit/{user}limit.txt")
    if file_name == False:
        limit = 0
        limitStr = str(limit)
        file = open(f"bumplimit/{user}limit.txt", "a+")
        file.write(limitStr)
        file.close()
    file = open(f"bumplimit/{user}limit.txt", "r")
    userLimit = file.readlines()
    file.close()
    userLimitInt = int(userLimit[0])
    return userLimitInt

def addUserLimit(user):
    userLimit = getUserLimit(user) + 1
    file = open(f"bumplimit/{user}limit.txt", "w")
    userLimitStr = str(userLimit)
    file.write(userLimitStr)
    file.close()

def getUserPrio(user):
    file_name = os.path.exists(f"bumps/{user}prio.txt")
    if file_name == False:
        prio = 0
        prioStr = str(prio)
        file = open(f"bumps/{user}prio.txt", "a+")
        file.write(prioStr)
        file.close()
    file = open(f"bumps/{user}prio.txt", "r")
    userPrio = file.readlines()
    file.close()
    userPrioInt = int(userPrio[0])
    return userPrioInt

def addUserPrio(user):
    userPrio= getUserPrio(user) + 1
    file = open(f"bumps/{user}prio.txt", "w")
    userPrioStr = str(userPrio)
    file.write(userPrioStr)
    file.close()
    addUserLimit(user)

def usePrio(user):
    userPrio= getUserPrio(user) - 1
    file = open(f"bumps/{user}prio.txt", "w")
    userPrioStr = str(userPrio)
    file.write(userPrioStr)
    file.close()
    addUserLimit(user)

def useBump(user):
    userBump = getUserBump(user) - 1
    file = open(f"bumps/{user}bump.txt", "w")
    userBumpStr = str(userBump)
    file.write(userBumpStr)
    file.close()
    addUserLimit(user)

def resetLimit():
    dir = "bumplimit/"
    for f in os.listdir(dir):
        os.remove(os.path.join(dir, f))

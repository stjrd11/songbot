import gspread
from gspread.models import Cell
from oauth2client.service_account import ServiceAccountCredentials
import urllib.request
import re
from datetime import date
from botconfig import *

scope = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)
songBank = client.open(spreadsheetName).sheet1
songHistory = client.open(spreadsheetName).worksheet(songHistory)

def next_available_row(worksheet):
    str_list = list(filter(None, worksheet.col_values(4)))
    return str(len(str_list)+1)

def updateSongBank(userRow, title, duration, user, url):
    cells = []
    cells.append(Cell(row=userRow, col=1, value=title))
    cells.append(Cell(row=userRow, col=2, value=duration))
    cells.append(Cell(row=userRow, col=3, value=user))
    cells.append(Cell(row=userRow, col=4, value=url))
    songBank.update_cells(cells)

def addToHistory(row, title, duration, user, url):
    cells = []
    value = []
    cells.append(Cell(row=row, col=1, value=title))
    cells.append(Cell(row=row, col=2, value=duration))
    cells.append(Cell(row=row, col=3, value=user))
    cells.append(Cell(row=row, col=4, value=url))
    cells.append(Cell(row=row, col=5, value=str(date.today())))
    songHistory.insert_row(value, 2)
    songHistory.update_cells(cells)

def bumpedSong(nextRow, title, duration, user, url):
    value = []
    cells = []
    cells.append(Cell(row=nextRow, col=1, value=title))
    cells.append(Cell(row=nextRow, col=2, value=duration))
    cells.append(Cell(row=nextRow, col=3, value=user))
    cells.append(Cell(row=nextRow, col=4, value=url))
    cells.append(Cell(row=nextRow, col=5, value="*BUMPED*"))
    songBank.insert_row(value, nextRow)
    songBank.update_cells(cells)

def findBumped():
    string1 = "*BUMPED*"
    cell = songBank.findall(string1)
    if len(cell):
        cellRow = cell[-1].row
        return cellRow
    else:
        return None

def prioBumpedSong(nextRow, title, duration, user, url):
    value = []
    cells = []
    cells.append(Cell(row=nextRow, col=1, value=title))
    cells.append(Cell(row=nextRow, col=2, value=duration))
    cells.append(Cell(row=nextRow, col=3, value=user))
    cells.append(Cell(row=nextRow, col=4, value=url))
    cells.append(Cell(row=nextRow, col=5, value="*PRIORITY BUMPED*"))
    songBank.insert_row(value, nextRow)
    songBank.update_cells(cells)

def findPrioBumped():
    string = "*PRIORITY BUMPED*"
    cell = songBank.findall(string)
    if len(cell):
        cellRow = cell[-1].row
        return cellRow
    else:
        return None

def entryToUrl(entry):
    if entry.find("watch?v=") != -1:
        return entry
    elif entry.find("youtu.be") != -1:
        return entry
    else:
        entry = entry.replace(" ","+")
        html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + entry)
        video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
        url = "https://www.youtube.com/watch?v=" + video_ids[0]
        return url

def getBumpInsert():
    prioBumpRow = findPrioBumped()
    bumpRow = findBumped()
    if prioBumpRow is None and bumpRow is None:
        bumpRow = 3
        return bumpRow
    elif prioBumpRow is None:
        bumpRow = bumpRow + 1
        return bumpRow
    elif bumpRow is None:
        nextRow = prioBumpRow + 1
        return nextRow
    else:
        bumpRow = bumpRow + 1
        return bumpRow

def getPrioInsert():
    prioBumpRow = findPrioBumped()
    if prioBumpRow is None:
        prioBumpRow = 3
        return prioBumpRow
    else:
        nextRow = prioBumpRow + 1
        return nextRow
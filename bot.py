from twitchio.ext import commands
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from botconfig import *
import csvmethods as csvm
import songrequest as srs
import bump as bmp
from gspread import Cell
from logging import Logger
from pytube import YouTube
import datetime
import time
import pandas as pd
import random

scope = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)
songBank = client.open(spreadsheetName).sheet1
songHistory = client.open(spreadsheetName).worksheet(songHistory)
queueOpen = 1

csvm.createBackup()

class Bot(commands.Bot):


    def __init__(self):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        # prefix can be a callable, which returns a list of strings or a string...
        # initial_channels can also be a callable which returns a list of strings...
        super().__init__(token=botAccessToken, prefix='!', initial_channels=[channel], case_insensitive=True)

    async def event_ready(self):
        # Notify us when everything is ready!
        # We are logged in and ready to chat and use commands...
        print(f'Logged in as | {self.nick}')

    async def event_message(self, message):
        # Messages with echo set to True are messages sent by the bot...
        # For now we just want to ignore them...
        if message.echo:
            return

        # Print the contents of our message to console...
        print(message.content)

        # Since we have commands and are overriding the default `event_message`
        # We must let the bot know we want to handle and invoke our commands...
        await self.handle_commands(message)

    @commands.command()
    async def ping(self, ctx: commands.Context):
        await ctx.send(f'🐍 Python online 🐍')

    @commands.command(name='sr', aliases=['request', 'songrequest'])
    async def sr(self, ctx:commands.Context, *, entry:str):
        try:
            user = ctx.author.name
            url = srs.entryToUrl(entry)
            yt = YouTube(url)
            title = yt.title
            duration = str(datetime.timedelta(seconds=yt.length))
            userLimit = bmp.getBumpsPlayedLimit(user)
            bumpCheck = bmp.getUserBump(user)
            prioCheck = bmp.getUserPrio(user)
            banCheck = csvm.banCheck(url)
            if ctx.author.is_mod:
                next = int(srs.next_available_row(songBank))
                srs.updateSongBank(next, title, duration, user, url)
                position = next - 1
                await ctx.send(f'{user}, your song, \"{title},\" has been added to the queue at position {position}')
            elif queueOpen == 0:
                await ctx.send(f'Sorry {user}, the queue is currently closed FeelsBadMan')
            elif yt.length > length:
                await ctx.send(f'{user}, that song is {duration}, the max length is {str(datetime.timedelta(seconds=length))} SeemsGood')
            elif yt.views < views:
                await ctx.send(f"{user}, song requests need more than {views} views SeemsGood")
            elif banCheck is True:
                await ctx.send(f'{user}, that song is banned.')
            else:
                cell_list = songBank.find(user)
                listCheck = songBank.findall(user)
                songCount = len(listCheck)
                checkList = songBank.find(url)
                if songCount >= maxSongsInQ:
                    await ctx.send(f"{user}, you can only have {maxSongsInQ} song(s) in the queue at a time SeemsGood")  
                elif cell_list is not None and cell_list.row != 2:
                    await ctx.send(f"{user}, you can only have {maxSongsInQ} song(s) in the queue at a time SeemsGood")   
                elif checkList is not None:
                    await ctx.send(f'{user}, that song is already in the queue!')
                elif prioCheck > 0 and userLimit < maxPlayedBumpsPerStream:
                    insertRow = srs.getPrioInsert()
                    srs.prioBumpedSong(insertRow, title, duration, user, url)
                    await ctx.send(f'{user}, your song, \"{title},\" has been priority bumped to position {insertRow - 1}')
                    print(bumpCheck)
                elif bumpCheck > 0 and userLimit < maxPlayedBumpsPerStream:
                    insertRow = srs.getBumpInsert()
                    srs.bumpedSong(insertRow, title, duration, user, url)
                    await ctx.send(f'{user}, your song, \"{title},\" has been bumped to position {insertRow - 1}')
                else:
                    next = int(srs.next_available_row(songBank))
                    srs.updateSongBank(next, title, duration, user, url)
                    position = next - 1
                    await ctx.send(f'{user}, your song, \"{title},\" has been added to the queue at position {position}')
        except Exception:
            await ctx.send(f'{user}, an error occured for some unknown reason. Try again.')
            Logger.exception("message")

    @commands.command()
    async def msr(self, ctx:commands.Context, *, entry:str):
        if ctx.author.is_mod:
            entry = entry.split(" ")
            url = entry[0]
            yt = YouTube(url)
            user = entry[1].lower()
            next = int(srs.next_available_row(songBank))
            title = yt.title
            duration = str(datetime.timedelta(seconds=yt.length))
            srs.updateSongBank(next, title, duration, user, url)
            await ctx.send(f'{user}, {ctx.author.name} has added your song to the queue for you, be sure to thank them!')
        
    @commands.command(name='edit', aliases=['change'])
    async def edit(self, ctx:commands.Context, *, entry:str):
        try:
            user = ctx.author.name
            url = srs.entryToUrl(entry)
            yt = YouTube(url)
            title = yt.title
            duration = str(datetime.timedelta(seconds=yt.length))
            cell = songBank.findall(user)
            if ctx.author.is_mod:
                userRow = cell[-1].row
                srs.updateSongBank(userRow, title, duration, user, url)
                await ctx.send(f'{user}, you have changed your song to \"{title}.\"')
            elif cell is None:
                await ctx.send(f'{user}, you don\'t have a song in the queue Jebaited')
            elif yt.length > length:
                await ctx.send(f'{user}, that song is {duration}, the max length is {str(datetime.timedelta(seconds=length))} SeemsGood')
            elif yt.views < views:
                await ctx.send(f"{user}, song requests need more than {views} views SeemsGood")
            else:
                checkList = songBank.find(url)
                if checkList is not None:
                    await ctx.send(f'{user}, that song is already in the queue!')
                else:
                    userRow = cell[-1].row
                    if userRow == 2:
                        await ctx.send(f'{user}, you can\'t change your song when it\'s currently playing.')
                    else:
                        srs.updateSongBank(userRow, title, duration, user, url)
                        await ctx.send(f'{user}, you have changed your song to \"{title}.\"')
        except Exception:
            await ctx.send(f'{user}, an error occured for some unknown reason. Try again')
            Logger.exception("message")

    @commands.command(name='wrongsong', aliases=['removesong'])
    async def wrongsong(self, ctx:commands.Context):
        user = ctx.author.name
        cell = songBank.findall(user)
        if cell is None:
            await ctx.send(f'{user}, you don\'t have a song in the queue Jebaited')
        else:
            userRow = cell[-1].row
            if userRow == 2:
                await ctx.send(f"{user}, your song might currently be playing! You can't delete it right now! D:")
            else:
                songBank.delete_rows(userRow)
                await ctx.send(f'{user}, your song has been deleted SeemsGood')

    @commands.command()
    async def remove(self, ctx:commands.Context, *, entry:str):
        if ctx.author.is_mod:
            entry = entry[0]
            entry = entry.lower()
            user = entry.replace("@", "")
            cell = songBank.findall(user)
            if cell is None:
                await ctx.send(f'{ctx.author.name}, {user} does not have a song in the queue.')
            else:
                userRow = cell[-1].row
                songBank.delete_rows(userRow)
                await ctx.send(f'{user}\'s song has been deleted.')

    @commands.command(name='song', aliases=['whatsong', 'whatsongisthis'])
    async def song(self, ctx:commands.Context):
        user = ctx.author.name
        values_list = songBank.row_values(2)
        await ctx.send(f'{user}, the current song is "{values_list[0]},\" requested by {values_list[2]}. {values_list[3]}')

    @commands.command()
    async def pn(self, ctx:commands.Context):
        if ctx.author.is_mod:
            nextRow = 2
            oldValues = songBank.row_values(2)
            srs.addToHistory(nextRow, oldValues[0], oldValues[1], oldValues[2], oldValues[3])
            values_list = songBank.row_values(3)
            if values_list[2] == oldValues[2]:
                if len(songBank.col_values(1)) > 3:
                    values_list = songBank.row_values(4)
                    cells = []
                    cells.append(Cell(row=nextRow, col=1, value=values_list[0]))
                    cells.append(Cell(row=nextRow, col=2, value=values_list[1]))
                    cells.append(Cell(row=nextRow, col=3, value=values_list[2]))
                    cells.append(Cell(row=nextRow, col=4, value=values_list[3]))
                    cells.append(Cell(row=nextRow, col=5, value="*NOW PLAYING*"))
                    songBank.update_cells(cells)
                    songBank.delete_rows(4)
                    if len(values_list) > 4:
                        if values_list[4] == "*PRIORITY BUMPED*":
                            bmp.usePrio(values_list[2])
                            bmp.addBumpsPlayedLimit(values_list[2])
                        elif values_list[4] == "*BUMPED*":
                            bmp.useBump(values_list[2])
                            bmp.addBumpsPlayedLimit(values_list[2])
                    songBank.update('E2', '*NOW PLAYING*')
                    await ctx.send(f'Back to back songs detected! Let\'s play someone elses first SeemsGood Now playing - {values_list[0]}, requested by \
                        {values_list[2]}. {values_list[3]}')
            else:
                songBank.delete_rows(2)
                if len(values_list) > 4:
                    if values_list[4] == "*PRIORITY BUMPED*":
                        bmp.usePrio(values_list[2])
                        bmp.addBumpsPlayedLimit(values_list[2])
                    elif values_list[4] == "*BUMPED*":
                        bmp.useBump(values_list[2])
                        bmp.addBumpsPlayedLimit(values_list[2])
                songBank.update('E2', '*NOW PLAYING*')
                await ctx.send(f'Now playing - {values_list[0]}, requested by {values_list[2]}. {values_list[3]}')

    @commands.command()
    async def skip(self, ctx:commands.Context):
        if ctx.author.is_mod:
            songBank.delete_rows(3)
            values_list = songBank.row_values(3)
            await ctx.send(f'Looks like we had to skip that song because that person isn\'t here (or that song ain\'t it Kappa ). {values_list[2]}, your song is up next!')

    @commands.command()
    async def when(self, ctx:commands.Context):
        user = ctx.author.name
        cell = songBank.find(user)
        if cell is None:
            await ctx.send(f'{user}, you don\'t have a song in the queue Jebaited')
        else:
            userRow = cell.row
            await ctx.send (f'{user}, you are in position {userRow - 1} in the queue.')

    @commands.command(name='next', aliases=['nextsong'])
    async def next(self, ctx:commands.Context):
        user = ctx.author.name
        values_list = songBank.row_values(3)
        await ctx.send(f'{user}, the next song will be "{values_list[0]},\" requested by {values_list[2]}.')

    @commands.command(name='last', aliases=['lastsong', 'whatsongwasthat'])
    async def last(self, ctx:commands.Context):
        user = ctx.author.name
        values_list = songHistory.row_values(2)
        await ctx.send(f'{user}, the last song played from the queue was "{values_list[0]},\" requested by {values_list[2]}. {values_list[3]}')

    @commands.command()
    async def oops(self, ctx:commands.Context):
        if ctx.author.is_mod:
            values_list = songHistory.row_values(2)
            songBank.insert_row(values_list, 2)
            songHistory.delete_rows(2)
            songBank.update('E2', '*NOW PLAYING*')
            await ctx.send('A mistake was made in the queue. Fixed.')

    @commands.command(name='list', aliases=['sl', 'songlist', 'queue', 'songqueue', 'q', 'sq'])
    async def list(self, ctx:commands.Context):
        await ctx.send(f'{ctx.author.name}, the song queue is here: {queueLink}')

    @commands.command()
    async def openq(self, ctx:commands.Context):
        if ctx.author.is_mod:
            global queueOpen
            queueOpen = 1
            await ctx.send(f'The queue is now open')

    @commands.command()
    async def closeq(self, ctx:commands.Context):
        if ctx.author.is_mod:
            global queueOpen
            queueOpen = 0
            await ctx.send(f'The queue is now closed')  

    @commands.command()        
    async def priobump(self, ctx:commands.Context, str:str):
        if ctx.author.is_mod:
            user = str.lower()
            cell1 = songBank.find(user)
            if cell1 is None:
                await ctx.send(f'{ctx.author.name}, {user} doesn\'t have a song in the queue.')
            else:
                userRow = cell1.row
                values_list = songBank.row_values(userRow)
                songBank.delete_rows(userRow)
                insertRow = srs.getPrioInsert()
                srs.prioBumpedSong(insertRow, values_list[0], values_list[1], values_list[2], values_list[3])
                await ctx.send(f'{user} has been bumped to position {insertRow - 1}')

    @commands.command()
    async def bigthanks(self, ctx:commands.Context, entry:str):
        if ctx.author.is_mod:
            user = entry.lower()
            cell1 = songBank.find(user)
            limit = bmp.getUserLimit(user)
            if limit >= maxBumpsPerStream:
                await ctx.send(f'Big thanks to {user}!')
            elif cell1 is None:
                bmp.addUserPrio(user)
                await ctx.send(f'Big thanks to {user}! Your song will be priority bumped when you request one!')
            else:
                bmp.addUserPrio(user)
                userRow = cell1.row
                values_list = songBank.row_values(userRow)
                songBank.delete_rows(userRow)
                insertRow = srs.getPrioInsert()
                srs.prioBumpedSong(insertRow, values_list[0], values_list[1], values_list[2], values_list[3])
                await ctx.send(f'Big thanks, {user}! Your song has been bumped to position {insertRow - 1}')

    @commands.command()
    async def bump(self, ctx:commands.Context, str:str):
        if ctx.author.is_mod:
            user = str.lower()
            cell1 = songBank.find(user)
            if cell1 is None:
                await ctx.send(f'{ctx.author.name}, {user} doesn\'t have a song in the queue.')
            else:
                userRow = cell1.row
                values_list = songBank.row_values(userRow)
                songBank.delete_rows(userRow)
                bumpInsertRow = srs.getBumpInsert()
                srs.bumpedSong(bumpInsertRow, values_list[0], values_list[1], values_list[2], values_list[3])
                await ctx.send(f'{user} has been bumped to position {bumpInsertRow - 1}.')
               
    @commands.command()
    async def thanks(self, ctx:commands.Context, str:str):
        if ctx.author.is_mod:
            user = str.lower()
            cell1 = songBank.find(user)
            cell2 = songBank.findall(user)
            songCount = len(cell2)
            limit = bmp.getUserLimit(user)
            if limit >= maxBumpsPerStream:
                await ctx.send(f'Thanks for the support, {user}!')
            elif cell1 is None:
                bmp.addUserBump(user)
                bmp.addUserLimit(user)
                await ctx.send(f'Thanks to {user}! Your song will be bumped when you request one!')
            elif cell1.row == 2 and songCount > 1:
                bmp.addUserBump(user)
                bmp.addUserLimit(user)
                userRow = cell2[-1].row
                values_list = songBank.row_values(userRow)
                songBank.delete_rows(userRow)
                bumpInsertRow = srs.getBumpInsert()
                srs.bumpedSong(bumpInsertRow, values_list[0], values_list[1], values_list[2], values_list[3])
                await ctx.send(f'Thanks, {user}! Your song has been bumped to position {bumpInsertRow - 1}.')
            elif cell1.row == 2:
                bmp.addUserBump(user)
                bmp.addUserLimit(user)
                await ctx.send(f'Thanks to {user}! Your song will be bumped when you request another one!')
            elif songBank.cell(cell1.row, 5).value == "*BUMPED*":
                await ctx.send(f'Thanks for the support, {user}!')
            else:
                bmp.addUserBump(user)
                bmp.addUserLimit(user)
                userRow = cell1.row
                values_list = songBank.row_values(userRow)
                songBank.delete_rows(userRow)
                bumpInsertRow = srs.getBumpInsert()
                srs.bumpedSong(bumpInsertRow, values_list[0], values_list[1], values_list[2], values_list[3])
                await ctx.send(f'Thanks, {user}! Your song has been bumped to position {bumpInsertRow - 1}.')

    @commands.command()
    async def extendo(self, ctx:commands.Context, str:str):
        if ctx.author.is_mod:
            user = str
            csvm.addUserExtended(user)
            await ctx.send(f'{user}, thanks for redeeming an extended song request. Please request it with !esr ')

    @commands.command()
    async def esr(self, ctx:commands.Context, url:str):
        user = ctx.author.name
        extend = csvm.getUserExtended(user)
        if extend > 0:
            yt = YouTube(url)
            title = yt.title
            duration = str(datetime.timedelta(seconds=yt.length))
            extendTime = str(datetime.timedelta(seconds=extendedLength))
            if yt.length > extendedLength:
                await ctx.send(f'{user}, that song is too long for an extended requested. The max length is {extendTime}\
                    , that song is {duration}.')
            else:
                bumpInsertRow = srs.getBumpInsert()
                srs.bumpedSong(bumpInsertRow, title, duration, user, url)
                position = bumpInsertRow - 1
                csvm.useExtend(user)
                await ctx.send(f'{user}, your song, \"{title},\" has been added to the queue at position {position}')
        else:
            await ctx.send(f'{user}, you don\'t have an extended song redemption D:')

    @commands.command()
    async def reset(self, ctx:commands.Context):
        if ctx.author.is_mod:
            bmp.resetLimit()
            oldValues = songBank.row_values(2)
            srs.addToHistory(2, oldValues[0], oldValues[1], oldValues[2], oldValues[3])
            await ctx.send ('Reset')
            songBank.clear()
            startUp = []
            startUp.append(Cell(row=1, col=1, value="Song"))
            startUp.append(Cell(row=1, col=2, value="Length"))
            startUp.append(Cell(row=1, col=3, value="Requester"))
            startUp.append(Cell(row=1, col=4, value="Link"))
            startUp.append(Cell(row=1, col=5, value="Other"))
            startUp.append(Cell(row=2, col=1, value="Stream Start"))
            startUp.append(Cell(row=2, col=2, value="--"))
            startUp.append(Cell(row=2, col=3, value="--"))
            startUp.append(Cell(row=2, col=4, value="https://www.twitch.tv/"))
            startUp.append(Cell(row=2, col=5, value="*NOW PLAYING*"))
            songBank.update_cells(startUp)

    @commands.command(name='doihaveabump', aliases=['gottabump', 'bumpcheck', 'czechrebumplic', 'bumplestillskin', 'bumplestiltskin', 'bumpkinpie', 'bumplebee'])
    async def doihaveabump(self, ctx:commands.Context):
        bumpCount = bmp.getUserBump(ctx.author.name)
        if bumpCount > 0:
            await ctx.send(f'{ctx.author.name}, you do have a bump')
        else:
            await ctx.send(f'{ctx.author.name}, you do not have a bump')

    @commands.command()
    async def bansong(self, ctx:commands.Context):
        if ctx.author.is_mod:
            values_list = songBank.row_values(2)
            df = pd.DataFrame({'link': [values_list[3]],
                                'user': [values_list[2]]})
            df.to_csv('bannedsongs.csv', mode='a', index=False, header=False)
            await ctx.send(f'{values_list[0]} has been added to the ban list.')

    @commands.command()
    async def savesong(self, ctx:commands.Context):
        if ctx.author.is_mod:
            values_list = songBank.row_values(2)
            user = values_list[2]
            df = pd.read_csv('savedSongs.csv')
            for i in range(len(df.link)):
                if [values_list[3]] == df.link[i]:
                    newValue = df.name[i] + " and " + user
                    df.at[i, 'name'] = newValue
                    df.to_csv('savedSongs.csv', index=False)
                    await ctx.send(f'{values_list[0]} has been saved.')
                else:
                    df = pd.DataFrame({'link':[values_list[3]],
                                        'time':[int(time.time())],
                                        'name':[values_list[2]]})
                    df.to_csv('savedSongs.csv', mode='a', index=False, header=False)
                    await ctx.send(f'{values_list[0]} has been saved.')

    @commands.command()
    async def randomsaved(self, ctx:commands.Context):
        if ctx.author.is_mod:
            df = pd.read_csv('savedSongs.csv', encoding="UTF8")
            rows = len(df.axes[0])
            randomNum = random.randint(0, rows)
            link = df.link[randomNum]
            seconds = df.time[randomNum]
            date = csvm.getDate(seconds)
            name = df.name(randomNum)
            user = 'Saved Song'
            yt = YouTube(link)
            title = yt.title
            duration = str(datetime.timedelta(seconds=yt.length))
            insertRow = srs.getBumpInsert()
            srs.bumpedSong(insertRow, title, duration, user, link)
            await ctx.send(f'Let\'s play a random saved song! How about {title}? This song was requested by {name} and saved on {date}.')

    @commands.command()
    async def randomize(self, ctx:commands.Context):
        if ctx.author.is_mod:
            songs = srs.next_available_row() - 1
            randomSong = random.randint(3,songs)
            values_list = songBank.row_values(randomSong)
            bumpRow = srs.getBumpInsert()
            srs.bumpedSong(bumpRow, values_list[0],values_list[1],values_list[2],values_list[3])
            await ctx.send(f'{values_list[2]}, your song has been chosen by the randomized gods!')

    @commands.command()
    async def startraffle(self, ctx:commands.Context):
        if ctx.author.is_mod:
            global joinAvail
            joinAvail = 1
            await ctx.send('A raffle has started for something. Please type !join to enter!')

    @commands.command()
    async def join(self, ctx:commands.Context):
        if joinAvail == 0:
            await ctx.send('There\'s no raffle right now Jebaited')
        else:
            user = ctx.author.name
            cell = songBank.find(user)
            if cell is None:
                await ctx.send(f'{user}, you must have a song in the queue before you can join a raffle.')
            elif cell.row == 2:
                await ctx.send(f'{user}, add another song to the queue before you join.')
            else:
                raffleCheck = csvm.checkRaffle(user)
                winnerCheck = csvm.checkWinner(user)
                if raffleCheck == 1:
                    await ctx.send(f'{user}, you\'re already in the raffle.')
                elif winnerCheck == 1:
                    await ctx.send(f'{user}, you just won a raffle. You have to wait until the next one to join.')
                else:
                    csvm.addToRaffle(user)
                    await ctx.send(f'{user}, you have been added to the raffle!')

    @commands.command()
    async def endprio(self, ctx:commands.Context):
        if ctx.author.is_mod:
            csvm.resetEligible()
            global joinAvail
            joinAvail = 0
            winner = csvm.getWinner()
            if winner == 0:
                await ctx.send(f'No one entered the raffle.')
            else:
                csvm.addRaffleWin(winner)
                csvm.resetRaffle()
                cell = songBank.find(winner)
                userRow = cell.row
                values_list = songBank.row_values(userRow)
                songBank.delete_rows(userRow)
                insertRow = srs.getPrioInsert()
                srs.prioBumpedSong(insertRow, values_list[0], values_list[1], values_list[2], values_list[3])
                await ctx.send(f'{winner} wins! You get a prio bump!')

    @commands.command()
    async def endbump(self, ctx:commands.Context):
        if ctx.author.is_mod:
            csvm.resetEligible()
            global joinAvail
            joinAvail = 0
            winner = csvm.getWinner()
            if winner == 0:
                await ctx.send(f'No one entered the raffle.')
            else:
                csvm.addRaffleWin(winner)
                csvm.resetRaffle()
                cell = songBank.find(winner)
                userRow = cell.row
                values_list = songBank.row_values(userRow)
                songBank.delete_rows(userRow)
                insertRow = srs.getBumpInsert()
                srs.bumpedSong(insertRow, values_list[0], values_list[1], values_list[2], values_list[3])
                await ctx.send(f'{winner} wins! You get a bump!')

    @commands.command()
    async def endraffle(self, ctx:commands.Context):
        if ctx.author.is_mod:
            csvm.resetEligible()
            global joinAvail
            joinAvail = 0
            winner = csvm.getWinner()
            if winner == 0:
                await ctx.send(f'No one entered the raffle.')
            else:
                csvm.addRaffleWin(winner)
                csvm.resetRaffle()
                await ctx.send(f'{winner} wins! You get NOTHING!')



bot = Bot()
bot.run()
# bot.run() is blocking and will stop execution of any below code here until stopped or closed.
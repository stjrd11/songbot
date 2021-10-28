import re
import twitchio
from twitchio.ext import commands
import os
from os.path import exists
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from gspread.models import Cell
import pafy
from datetime import date
import urllib.request


scope = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('insertyourauthetnicationfileshere.json', scope)
client = gspread.authorize(creds)

songBank = client.open("insertyoursheethere").sheet1
songHistory = client.open("yoursheet").worksheet("yoursheet")

queueOpen = 1


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
    cells.append(Cell(row=row, col=1, value=title))
    cells.append(Cell(row=row, col=2, value=duration))
    cells.append(Cell(row=row, col=3, value=user))
    cells.append(Cell(row=row, col=4, value=url))
    cells.append(Cell(row=row, col=5, value=str(date.today())))
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
    string = "*BUMPED*"
    cell = songBank.findall(string)
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



class Bot(commands.Bot):


    def __init__(self):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        # prefix can be a callable, which returns a list of strings or a string...
        # initial_channels can also be a callable which returns a list of strings...
        super().__init__(token='yourtokenhere', prefix='!', initial_channels=['yourchannelhere'])

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
    async def hello(self, ctx: commands.Context):
        # Here we have a command hello, we can invoke our command with our prefix and command name
        # e.g !hello
        # We can also give our commands aliases (different names) to invoke with.

        # Send a hello back!
        # Sending a reply back to the channel is easy... Below is an example.
        await ctx.send(f'Hello {ctx.author.name}!')

    @commands.command(name='sr', aliases=['request', 'songrequest'])
    async def sr(self, ctx:commands.Context, *, entry:str):
        user = ctx.author.name
        entry = entry.replace(" ","+")
        html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + entry)
        video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
        url = "https://www.youtube.com/watch?v=" + video_ids[0]
        video = pafy.new(url)
        cell_list = songBank.find(user)
        checkList = songBank.find(url)
        if user == 'slamthejam11':
            next = int(next_available_row(songBank))
            title = video.title
            duration = video.duration
            updateSongBank(next, title, duration, user, url)
            await ctx.send(f'{user}, your song, \"{title},\" has been added to the queue at position {next}')
        elif queueOpen == 0:
            await ctx.send(f'Sorry {user}, the queue is currently closed FeelsBadMan')
            print(queueOpen)
        elif cell_list is not None and cell_list.row != 1:
            await ctx.send(f'{user}, you already have a song in the queue.')
        elif video.length > 395:
            await ctx.send(f'{user}, that song is {video.duration}, the max length is 06:35 SeemsGood')
        elif checkList is not None:
            await ctx.send(f'{user}, that song is already in the queue!')        
        else:
            next = int(next_available_row(songBank))
            title = video.title
            duration = video.duration
            updateSongBank(next, title, duration, user, url)
            await ctx.send(f'{user}, your song, \"{title},\" has been added to the queue at position {next}')
        
    @commands.command(name='edit', aliases=['change'])
    async def edit(self, ctx:commands.Context, *, entry:str):
        user = ctx.author.name
        entry = entry.replace(" ","+")
        html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + entry)
        video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
        url = "https://www.youtube.com/watch?v=" + video_ids[0]
        video = pafy.new(url)
        cell = songBank.find(user)
        checkList = songBank.find(url)
        if user == 'slamthejam11':
            userRow = cell.row
            title = video.title
            duration = video.duration
            updateSongBank(userRow, title, duration, user, url)
            await ctx.send(f'{user}, you have changed your song to \"{title}.\"')
        elif cell is None:
            await ctx.send(f'{user}, you don\'t have a song in the queue Jebaited')
        elif video.length > 395:
            await ctx.send(f'{user}, that song is {video.duration}, the max length is 06:35 SeemsGood')
        elif checkList is not None:
            await ctx.send(f'{user}, that song is already in the queue!')
        else:
            userRow = cell.row
            title = video.title
            duration = video.duration
            updateSongBank(userRow, title, duration, user, url)
            await ctx.send(f'{user}, you have changed your song to \"{title}.\"')

    @commands.command(name='wrongsong', aliases=['remove', 'removesong'])
    async def wrongsong(self, ctx:commands.Context):
        user = ctx.author.name
        cell = songBank.find(user)
        if cell is None:
            await ctx.send(f'{user}, you don\'t have a song in the queue Jebaited')
        else:
            userRow = cell.row
            songBank.delete_row(userRow)
            await ctx.send(f'{user}, your song has been deleted SeemsGood')

    @commands.command(name='song', aliases=['whatsong', 'whatsongisthis'])
    async def song(self, ctx:commands.Context):
        user = ctx.author.name
        values_list = songBank.row_values(1)
        await ctx.send(f'{user}, the current song is "{values_list[0]},\" requested by {values_list[2]}. {values_list[3]}')

    @commands.command()
    async def pn(self, ctx:commands.Context):
        if ctx.author.name == 'slamthejam11':
            nextRow = int(next_available_row(songHistory))
            oldValues = songBank.row_values(1)
            addToHistory(nextRow, oldValues[0], oldValues[1], oldValues[2], oldValues[3])
            songBank.delete_rows(1)
            values_list = songBank.row_values(1)
            await ctx.send(f'Now playing - {values_list[0]}, requested by {values_list[2]}. {values_list[3]}')
        else:
            await ctx.send(f'{ctx.author.name}, you\'re not Slam peepoWTF')

    @commands.command()
    async def when(self, ctx:commands.Context):
        user = ctx.author.name
        cell = songBank.find(user)
        if cell is None:
            await ctx.send(f'{user}, you don\'t have a song in the queue Jebaited')
        else:
            userRow = cell.row
            await ctx.send (f'{user}, you are in position {userRow} in the queue.')

    @commands.command(name='next', aliases=['nextsong'])
    async def next(self, ctx:commands.Context):
        user = ctx.author.name
        values_list = songBank.row_values(2)
        await ctx.send(f'{user}, the next song will be "{values_list[0]},\" requested by {values_list[2]}.')

    @commands.command(name='last', aliases=['lastsong', 'whatsongwasthat'])
    async def last(self, ctx:commands.Context):
        user = ctx.author.name
        lastRow = int(next_available_row(songHistory))
        lastRow = lastRow - 1
        values_list = songHistory.row_values(lastRow)
        await ctx.send(f'{user}, the last song Slam played from the queue was "{values_list[0]},\" requested by {values_list[2]}. {values_list[3]}')

    @commands.command(name='list', aliases=['sl', 'songlist', 'queue', 'songqueue'])
    async def list(self, ctx:commands.Context):
        await ctx.send(f'{ctx.author.name}, the song queue is here: insertyourlink')

    @commands.command()
    async def openq(self, ctx:commands.Context):
        user = ctx.author.name
        if user == 'slamthejam11':
            global queueOpen
            queueOpen = 1
            await ctx.send(f'The queue is now open')
        else:
            await ctx.send(f'Top of the morning.')

    @commands.command()
    async def closeq(self, ctx:commands.Context):
        user = ctx.author.name
        if user == 'slamthejam11':
            global queueOpen
            queueOpen = 0
            await ctx.send(f'The queue is now closed')
        else:
            await ctx.send(f'Top of the morning.')    

    @commands.command()        
    async def priobump(self, ctx:commands.Context, str:str):
        if ctx.author.name =='slamthejam11':
            user = str.lower()
            cell1 = songBank.find(user)
            if cell1 is None:
                await ctx.send(f'{ctx.author.name}, {user} doesn\'t have a song in the queue.')
            else:
                userRow = cell1.row
                values_list = songBank.row_values(userRow)
                cell2 = findPrioBumped()
                songBank.delete_rows(userRow)
                if cell2 is None:
                    prioBumpedSong(1, values_list[0], values_list[1], values_list[2], values_list[3])
                    await ctx.send(f'{user} has been bumped to position 1.')
                else:
                    nextRow = cell2 + 1
                    prioBumpedSong(nextRow, values_list[0], values_list[1], values_list[2], values_list[3])
                    await ctx.send(f'{user} has been bumped to position {nextRow}.')
        else:
            await ctx.send("No.")

    @commands.command()
    async def bump(self, ctx:commands.Context, str:str):
        if ctx.author.name =='slamthejam11':
            user = str.lower()
            cell1 = songBank.find(user)
            if cell1 is None:
                await ctx.send(f'{ctx.author.name}, {user} doesn\'t have a song in the queue.')
            else:
                userRow = cell1.row
                values_list = songBank.row_values(userRow)
                prioBumpRow = findPrioBumped()
                bumpRow = findBumped()
                songBank.delete_rows(userRow)
                if prioBumpRow is None and bumpRow is None:
                    bumpedSong(1, values_list[0], values_list[1], values_list[2], values_list[3])
                    await ctx.send(f'{user} has been bumped to position 1.')
                elif prioBumpRow is None:
                    bumpRow = bumpRow + 1
                    bumpedSong(bumpRow, values_list[0], values_list[1], values_list[2], values_list[3])
                    await ctx.send(f'{user} has been bumped to position {bumpRow}.')
                elif bumpRow is None:
                    nextRow = prioBumpRow + 1
                    bumpedSong(nextRow, values_list[0], values_list[1], values_list[2], values_list[3])
                    await ctx.send(f'{user} has been bumped to position {nextRow}.')
                else:
                    bumpRow = bumpRow + 1
                    bumpedSong(bumpRow, values_list[0], values_list[1], values_list[2], values_list[3])
                    await ctx.send(f'{user} has been bumped to position {bumpRow}.')
        else:
            await ctx.send("No.")
            




bot = Bot()
bot.run()
# bot.run() is blocking and will stop execution of any below code here until stopped or closed.

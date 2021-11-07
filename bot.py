from twitchio.ext import commands
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import pafy
from botconfig import *
import songrequest as srs
import bump as bmp


scope = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)
songBank = client.open(YOUR_QUEUE_SHEET_HERE).sheet1
songHistory = client.open(YOUR_QUEUE_SHEET_HERE).worksheet(YOUR_HISTORY_SHEET_HERE)
queueOpen = 1


class Bot(commands.Bot):


    def __init__(self):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        # prefix can be a callable, which returns a list of strings or a string...
        # initial_channels can also be a callable which returns a list of strings...
        super().__init__(token=botAccessToken, prefix='!', initial_channels=[YOURCHANNEL])

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

    @commands.command(name='sr', aliases=['request', 'songrequest'])
    async def sr(self, ctx:commands.Context, *, entry:str):
        user = ctx.author.name
        url = srs.entryToUrl(entry)
        video = pafy.new(url)
        userLimit = bmp.getUserLimit(user)
        bumpCheck = bmp.getUserBump(user)
        prioCheck = bmp.getUserPrio(user)
        if ctx.author.is_mod:
            next = int(srs.next_available_row(songBank))
            title = video.title
            duration = video.duration
            srs.updateSongBank(next, title, duration, user, url)
            position = next - 1
            await ctx.send(f'{user}, your song, \"{title},\" has been added to the queue at position {position}')
        elif queueOpen == 0:
            await ctx.send(f'Sorry {user}, the queue is currently closed FeelsBadMan')
        elif video.length > 395:
            await ctx.send(f'{user}, that song is {video.duration}, the max length is 06:35 SeemsGood')
        else:
            cell_list = songBank.find(user)
            checkList = songBank.find(url)
            if cell_list is not None and cell_list.row != 2:
                await ctx.send(f'{user}, you already have a song in the queue.')      
            elif checkList is not None:
                    await ctx.send(f'{user}, that song is already in the queue!')
            elif prioCheck > 0 and userLimit < 2:
                insertRow = srs.getPrioInsert()
                title = video.title
                duration = video.duration
                srs.prioBumpedSong(insertRow, title, duration, user, url)
                await ctx.send(f'{user}, your song, \"{title},\" has been priority bumped to position {insertRow - 1}')
                print(bumpCheck)
            elif bumpCheck > 0 and userLimit < 2:
                insertRow = srs.getBumpInsert()
                title = video.title
                duration = video.duration
                srs.bumpedSong(insertRow, title, duration, user, url)
                await ctx.send(f'{user}, your song, \"{title},\" has been bumped to position {insertRow - 1}')
            else:
                next = int(srs.next_available_row(songBank))
                title = video.title
                duration = video.duration
                srs.updateSongBank(next, title, duration, user, url)
                position = next - 1
                await ctx.send(f'{user}, your song, \"{title},\" has been added to the queue at position {position}')
        
    @commands.command(name='edit', aliases=['change'])
    async def edit(self, ctx:commands.Context, *, entry:str):
        user = ctx.author.name
        url = srs.entryToUrl(entry)
        video = pafy.new(url)
        cell = songBank.find(user)
        if ctx.author.is_mod:
            userRow = cell.row
            title = video.title
            duration = video.duration
            srs.updateSongBank(userRow, title, duration, user, url)
            await ctx.send(f'{user}, you have changed your song to \"{title}.\"')
        elif cell is None:
            await ctx.send(f'{user}, you don\'t have a song in the queue Jebaited')
        elif video.length > 395:
            await ctx.send(f'{user}, that song is {video.duration}, the max length is 06:35 SeemsGood')
        else:
            checkList = songBank.find(url)
            if checkList is not None:
                await ctx.send(f'{user}, that song is already in the queue!')
            else:
                userRow = cell.row
                title = video.title
                duration = video.duration
                srs.updateSongBank(userRow, title, duration, user, url)
                await ctx.send(f'{user}, you have changed your song to \"{title}.\"')

    @commands.command(name='wrongsong', aliases=['remove', 'removesong'])
    async def wrongsong(self, ctx:commands.Context):
        user = ctx.author.name
        cell = songBank.find(user)
        if cell is None:
            await ctx.send(f'{user}, you don\'t have a song in the queue Jebaited')
        else:
            userRow = cell.row
            songBank.delete_rows(userRow)
            await ctx.send(f'{user}, your song has been deleted SeemsGood')

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
            songBank.delete_rows(2)
            values_list = songBank.row_values(2)
            if values_list[4] == "*PRIORITY BUMPED*":
                bmp.usePrio(values_list[2])
                bmp.addUserLimit(values_list[2])
            elif values_list[4] == "*BUMPED*":
                bmp.useBump(values_list[2])
                bmp.addUserLimit(values_list[2])
            songBank.update('E2', '*NOW PLAYING*')
            await ctx.send(f'Now playing - {values_list[0]}, requested by {values_list[2]}. {values_list[3]}')

    @commands.command()
    async def skip(self, ctx:commands.Context):
        if ctx.author.is_mod:
            songBank.delete_rows(2)
            values_list = songBank.row_values(2)
            songBank.update('E2', '*NOW PLAYING*')
            await ctx.send(f'Looks like we had to skip that song because that person isn\'t here (or the song was no good Kappa ). Now Playing - {values_list[0]}, requested by \
                {values_list[2]}. {values_list[3]}')

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
        values_list = songBank.row_values(3)
        await ctx.send(f'{user}, the next song will be "{values_list[0]},\" requested by {values_list[2]}.')

    @commands.command(name='last', aliases=['lastsong', 'whatsongwasthat'])
    async def last(self, ctx:commands.Context):
        user = ctx.author.name
        values_list = songHistory.row_values(2)
        await ctx.send(f'{user}, the last song Slam played from the queue was "{values_list[0]},\" requested by {values_list[2]}. {values_list[3]}')

    @commands.command(name='list', aliases=['sl', 'songlist', 'queue', 'songqueue'])
    async def list(self, ctx:commands.Context):
        await ctx.send(f'{ctx.author.name}, the song queue is here: insert link')

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
            if limit > 2:
                await ctx.send(f'Big thanks to {user}!')
            elif cell1 is None:
                bmp.addUserPrio(user)
                await ctx.send(f'Big thanks to {user}! Your song will be priority bumped when you request one!')
            else:
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
            limit = bmp.getUserLimit(user)
            if limit > 2:
                await ctx.send(f'Thanks for the support, {user}!')
            elif cell1 is None:
                bmp.addUserBump(user)
                await ctx.send(f'Thanks to {user}! Your song will be bumped when you request one!')
            else:
                userRow = cell1.row
                values_list = songBank.row_values(userRow)
                songBank.delete_rows(userRow)
                bumpInsertRow = srs.getBumpInsert()
                srs.bumpedSong(bumpInsertRow, values_list[0], values_list[1], values_list[2], values_list[3])
                await ctx.send(f'Thanks, {user}! Your song has been bumped to position {bumpInsertRow - 1}.')

    @commands.command()
    async def resetlimit(self, ctx:commands.Context):
        if ctx.author.is_mod:
            bmp.resetLimit()
            await ctx.send ('Bump limits have been reset.')


bot = Bot()
bot.run()
# bot.run() is blocking and will stop execution of any below code here until stopped or closed.

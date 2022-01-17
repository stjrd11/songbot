# songbot

## About

This is a songbot I built using Twitchio, Gspread, and Pytube libraries in Python, along with Twurple in Node.js. This bot is meant to generally replace/relieve mods/streamers from modding a queue in a music stream on Twitch, although you can use it as any sort of queue system for videos in a stream. It can automatically bump requests on a bump/raid/cheer. Please note that this bot is NOT meant to totally replace a more complete streaming bot like StreamElements/StreamLabs/etc., but more to complement/replace the queue system.

If you run into any issues, please either post on Github or contact me through discord: Slam#1253

## Video Guide

Coming soon

## Installation

1. Install anaconda here: https://docs.anaconda.com/anaconda/install/index.html  follow installation instructions (can be defaulted, no need to change anything)
2. Install node.js here: https://nodejs.org/en/download/ follow installation instructions (no need for extra stuff, can be defaulted)
3. Install vs code here: https://code.visualstudio.com/download follow instructions
4. Download code from github: https://github.com/stjrd11/songbot  (Code -> Download Zip) and unzip into a folder
5. Open Anaconda Prompt (type anaconda into the windows search bar and look for Anaconda Prompt).
  * First, navigate to the directory where you unzipped your songbot folder (for example, if you unzipped your songbot folder in a folder called twitch, then type 'cd/twitch/songbot-main'
  * Next, type 'pip install -r requirements.txt'
6. Open the command prompt by typing cmd into the windows search bar. Type the following two lines into the prompt:
  * Npm install @twurple/auth
  * Npm install @twurple/chat
7. Go to https://console.developers.google.com/ and create a new project.
  * In the box labeled “Search for APIs and Services” search for Google Drive API and Google Sheets API and enable them both.
  * Go to APIS & Services, then go to “Credentials.” Choose “Create credentials > Service account”
  * Fill out form. Name can be anything, Role should be editor, and no need to grant anyone else access to the account. Click Done.
  * Go to “Manage Service Accounts” above Service Accounts.
  * Press on the three vertical dots near the recently created service account and select “Manage keys” then click “Add key > Create new key”
  * Select JSON key type and press create. Save this new .json file in the same folder where the song bot is, and rename it to ‘credentials.json’
8. Go to Google Sheets: https://www.google.com/sheets/about/ 
  * Create a blank sheet and call it SongBank or something similar. Inside, you will make two separate sheets. One for the queue, and one for the History. On the bottom, create a new sheet. Label the first one “Queue” or something similar, and the second one as “SongHistory” or something similar.
  * On the “Queue” sheet, label the following cells:
    * A1: Song
    * B1: Length
    * C1: Requester
    * D1: Link
    * E1: Other
  * On the “SongHistory” sheet, label the following cells:
    * A1: Song
    * B1: Length
    * C1: Requester
    * D1: Link
    * E1: Date
  * Finally, share the spreadsheet with the client_email. Make sure it is shared with editor permissions.
9. Get credentials from this site: https://twitchtokengenerator.com/ You just need a regular bot chat token. Make sure you get the credentials under the account you want the bot to speak through. You can use your own account, or a bot account. C/P the access token and refresh token somewhere safe for later.
10. Go to the Twitch Development website https://dev.twitch.tv/console/apps and register a new application
  * Name: Whatever you want it to be
  * OAuth Redirect URLs: http://localhost 
  * Category: Chat bot
  * Click ‘manage’ on your application, and you should see a ‘Client ID’ and ‘Client Secret’. We will use those soon.
11. Open VS Code and open the folder where the song bot is.
  * We will first modify botconfig.py
    * botAccessToken: This is the token from the credentials site earlier. You need the Access token.
    * maxBumpsPerStream: This is how many bumps a user can get per stream (or per run of the bot, if you want to be technical) from the automated !thanks command. Once a user hits this limit, !thanks will just thank them and not give a bump. This is set to 2 for my bot.
    * maxPlayedBumpsPerStream: This is how many times the bot will automatically bump a song from a user per stream (or per run of the bot). For my version, it is also set to 2.
    * maxStoredBumps: This is how many bumps can be stored for a user. I set this to 1 for my bot.
    * maxStoredPrio: This is how many priority bumps can be stored for a user. I set this to 1 for my bot.
    * maxSongsInQ = This is how many songs a user can have in the queue at once. I set this to 1 on my version, and I recommend keeping it at 1 as that how it was designed. Some commands may not work properly if this is grater than 1.
    * spreadsheetName = This is the name of the spreadsheet in Google sheets.
    * songBank = This is the name of the queue sheet in Google Sheets.
    * songHistory = This is the name of the history sheet in Google Sheets.
    * channel = This is the name of the Twitch channel the bot will be joining.
    * length = Maximum length of the song (in seconds) that a user can request.
    * views = Minimum amount of views that a YouTube video needs to be requested.
    * extendedLength = Maximum length for an extended request. This is optional, if you don’t want extended requests on your channel, just set this to a large number, like 9999
    * queueLink = The link to your google spreadsheet. Make sure the link you share is a view-only link, not an editor link. Also recommended to shorten the link with a url shortener, like at https://www.shorturl.at/ 
  * Next, open up nodeconfig.js and fill out info
    * CLIENTID = Client ID from the application on the Twitch Dev website
    * CLIENTSECRET = Client secret from the application on the Twitch Dev website
    * CHANNEL = the channel the bot will be joining.
    * BITTHRESHOLD = Minimum number of bits to for the bot to bump someone. Mine is set to 300.
    * RAIDCOUNT = Minimum number of people in a raid for the bot to priority bump a song. Mine is set to 5.
  * Next, open up tokens.json and fill in access token and refresh token from generator site.

The song bot is now ready to start. Open up a command prompt and an anaconda prompt. Navigate to the folder where the files are located using the ‘cd’ command in BOTH prompts (example: if your songbot folder is in a folder called ‘Twitch’, you would use the command ‘cd twitch/songbot’ to get to the folder). For the anaconda prompt, type ‘python bot.py’ and for the command prompt, type ‘node nodebot.js’
Both portions of the bot should now be running. Make a batch command to avoid having to open prompts and change directories (see end of tutorial installation video for more details)

## Commands List

* !ping – Just a way to make sure the bot is connected. If !ping works, the bot is connected.
* !sr – This is used to request songs to put in the queue. It works with either a direct YouTube link or a song name (!sr rush tom sawyer OR !sr https://www.youtube.com/watch?v=dQw4w9WgXcQ). It checks if the queue is open, length, views, and if the song is either on the ban list or already in the queue.
  * Aliases - !request, !songrequest
  * NOTE: Channel mods are immune to all restrictions for song requests. There are a few reasons for this, but just be sure your mods are aware of this.
* !msr – This is similar to !sr, but it allows a mod to request a song FOR someone else, either because they can’t figure it out themselves or a stream has gone off the rails. A direct YouTube link needs to be used, it will not work otherwise. 
  * Example: '!msr https://www.youtube.com/watch?v=dQw4w9WgXcQ slamthejam11' will request that song under the name slamthejam11
* !edit – Lets a user change their song. Still checks against all restrictions.
  * Alias - !change
  * Example - !edit audioslave like a stone
* !wrongsong – Removes a users song from the queue
  * Alias - !removesong
* !remove – A mod only command that removes someone elses song (either due to bad song or they can’t figure anything out)
  * Example - !removesong slamthejam11
* !song – Tells the user what song is currently playing in the queue.
* !pn – Mod only command that moves the queue forward. The song in the Now Playing row gets move to history, and the next song is moved up into Now Playing. 
* !skip – Removes the song in Row 3 (the Up Next row). Ideally, you would use this if that person is not there to hear their song, or you recognize that the requested song is not something you wan to play.
* !when – Tells a user where in the queue their song is
* !next – Tells a user what the next song in the queue is
  * Alias - !nextsong
* !last – Tells a user what the last song played was
  * Alias - !lastsong, !whatsongwasthat
* !oops – A mod-only command that can be used if !pn is accidentally used too many times, or a song is skipped on accident. It takes the first song in the history and adds it to the Now Playing row, and pushes the rest of the queue down 1.
* !list – Gives a link to the queue.
  * Alias - !sl, !songlist, !queue, !songqueue, !q, !sq
* !openq – Opens the queue for song requests. The queue is open by default when the songbot is started up.
* !closeq – Closes the queue and no longer allows song requests (users can still edit their songs.)
* !priobump –A mod-only command that priority bumps a users song to the top of the queue. This command does not take into account if the user has hit their prio bump limit for the stream.
  * Example - !priobump slamthejam11
* !bigthanks – Same as !priobump, except it does check if the user has reached their prio bump limit. This command is only automated during raids. If someone raids your stream with the minimum amount of required viewers, the bot will automatically give them a !bigthanks, which means when they request a song, it will be priority bumped.
* !bump – Mod-only command that bumps a users song in the queue. This command does not take into account if the user has hit their bump limit for the stream.
* !thanks – Same as !bump but it does take into account if a bump limit has been reached. This command will fire off automatically on subs, resubs, gift subs, and if the bit threshold is reached on a cheer. This command cannot fire off on direct money donations through streamelements/streamlabs/etc.
* !extendo – mod only command that gives a user a “token” for an extended song request. Ignore this command if you don’t allow for extended songs in your stream.
  * Example - !extendo slamthejam11
* !esr – Similar to !sr, except allows a user to request an extended request if they have a token for it.
* !reset – Mod only command that resets bump limits and clears the queue. Use this when the stream is over (or you just want to reset the queue system).
* !doihaveabump – Allows a user to check if they have a bump.
  * Alias - !gottabump, !bumpcheck, !czechrebumplic, !bumplestillskin, !bumplestiltskin, !bumpkinpie, !bumplebee
* !bansong – Mod only command that adds what the currently playing song is to a ban list, which disallows the song to be requested again.
* !savesong – Mod only command that adds what the currently playing song is to a saved list. The link, date requested, and name of the requester is stored in a .csv called savedSongs
* !randomsaved – Mod only command that adds a random saved song to the queue and bumps it.
* !randomize – Mod only command that takes a random song in the queue and bumps it
* !startraffle – Mod only command that starts a raffle
* !join – Command that allows a user to join the raffle. They cannot join a raffle if they won the most recent raffle. They must also have a song in the queue to join a raffle.
* !endprio – Mod only command that ends the raffle, and the winner gets a priority bump.
* !endbump – Mod only command that ends the raffle, and the winner gets a bump.
* !endraffle – Mod only command that ends the raffle, and the winner gets nothing (or your own reward, but the bot doesn’t give them anything.

**Credits

Big thanks to the developers of Gspread, Pytube, Twurple, and TwitchIO (especially the folks on the Pythonista discord server for answering my dumb questions). Also thanks to pretzel for being my beta tester, and to jonandjosh for letting me use their stream as a test bed.

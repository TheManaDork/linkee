startup_errors = []
database = None
TOKEN = None
ADMIN = None
global_settings = {"enable":True}

#==================Error Logging Imports====================
import traceback

#==================Settings====================
error_logging_channel = 1499507490436677813
error_logging_obj = None
# devchannel_id = 1279148032142868593


#==================Error Logger============================
def set_up_log():
    global error_logging_obj
    error_logging_obj = client.get_channel(error_logging_channel)

def log_format(details="",channel="",level=0,error=True):
    other_info = str(details)
    if other_info:
        other_info = f"\nOther info: {other_info}"
    if channel:
        try:
            channel = f"\nChannel ID: {channel.id}; Channel Name: {channel.name}; Guild ID: {channel.guild.id}; Guild Name: {channel.guild.name}"
        except Exception as e:
            channel = f"\nError getting channel ID. Channel input = {channel}\nLogging error: {e}"
    if error:
        out=f':x: ERROR (Asby V2):\n```{traceback.format_exc()}```{channel}{other_info}'
    else:
        out=f':green_circle: LOG (Asby V2):\n```{traceback.format_exc()}```{channel}{other_info}'
    return out

async def log(details="",channel="",level=0,error=True):
    await error_logging_obj.send(log_format(details,channel,level,error))


#==================Import Libs======================

import os
import sys
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv


#==================Variable Inits==================-


load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
ADMIN = str(os.getenv("OPPED_USER"))

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

client = discord.Client(intents=intents)



#==================Import Helper Libs======================
try:
    import sqlite3
except:
    startup_errors.append(log_format(f'Error importing lib sqlite3.'))

try:
    import csv
except:
    startup_errors.append(log_format(f'Error importing lib csv.'))

try:
    import requests
except:
    startup_errors.append(log_format(f'Error importing lib requests'))



 #========================== Command Methods =====================================================

async def command_uploadLinks(message):
    if str(message.author.id) != ADMIN:
        await message.channel.send("You do not have the permissions to use this command")
        return

    if len(message.attachments) != 1:
        await message.channel.send("Command must be sent with one attachment")
        return

    r = requests.get(message.attachments[0].url)

    links = r.text.split('\n')
    links = [link.strip() for link in links if link.strip()]

    # for link in links:
    #     print(f"{link}\n")

    with database:
        for link in links:
            database.execute("INSERT INTO tickets (link, used) VALUES (?,?)", (link, False))

    print(f"Added {len(links)} links to tickets")
    await message.channel.send(f"Added {len(links)} links!")


async def command_uploadAsbesties(message):
    if str(message.author.id) != ADMIN:
        await message.channel.send("You do not have the permissions to use this command")
        return

    if len(message.attachments) != 1:
        await message.channel.send("Command must be sent with one attachment")
        return
    r = requests.get(message.attachments[0].url)
    IDs = r.text.split('\n')
    IDs = [ID.strip() for ID in IDs if ID.strip()]

    with database:
        for ID in IDs:
            if not ID.isnumeric():
                print(ID)
                continue
            database.execute("INSERT INTO asbesties (id) VALUES (?)", (ID,))

    print(f"Added {len(IDs)} IDs!")
    await message.channel.send(f"Added {len(IDs)} IDs!")


async def command_vote(message):
    print("voting...", flush=True)
    try:
        # check environment
        if isinstance(message.author, discord.User):
            print("Is private!", flush=True)
        else:
            print("WARNING: Is public", flush=True)
            await message.channel.send("ERROR: Command can only be used in DM's.")
            return

        # check user is an asbestie
        output = database.execute("SELECT id FROM asbesties WHERE id=?", (str(message.author.id),)).fetchall()

        if len(output) < 1:
            await message.channel.send("""
                You must be a member of the Asbestos Pool Swimming Club in order to vote. 
                If you feel that you are a member of the Asbestos Pool Swimming Club, please reach out to the organizers of this election.
                """)
            return

        # check user has not voted before
        output = database.execute("SELECT id FROM voters WHERE id=?", (str(message.author.id),)).fetchall()

       
        if len(output) > 0:
            await message.channel.send(""" 
                You have already received your voting link. You cannot get another one. If you were unable to vote with the link you were given or if this is the first time you have requested a link, please contact Graydon Bush, username TheManaDorh
                """)
            return

        # retrieve voting link and mark link as used
        output = database.execute("UPDATE tickets SET used = TRUE WHERE link = (SELECT link FROM tickets WHERE used = FALSE LIMIT 1) RETURNING link;").fetchone()

        if output == None:
            await message.channel.send("""
                It seems we have run out of voting tickets. If you have not yet voted and feel you should get to, please reach out to those in charge of this vote.
                """)
            return

        link = output[0]

        await message.channel.send(f"""
Click [here](<{link}>) to vote!

NOTE: This is the only link you can receive via this command. If this link says it has already been used or otherwise is not working then please contact 
Those in charge of this vote. Due to the need to preserve privacy, anonymity, and preventing cheating, there is no good way for us to know your link is broken,
If you have voted or not, or help you vote if you don't find someone in person and show this to them.

The decisions you make while filling out this form are entirely anonymous and should not be shared with anyone.
For details on the system of voting we are using please use the command '/info'

-# We at the Asbestos Management Team are legally not liable for any damages to life, limb, or marriage contracts as a result of clicking the above link
-# Known side effects include: democracy, Emma, golden honmoon, the Demon King declaring victory, acne, pregnancy, sudden heart attack, an odd feeling of weightlessness
            """)

        # mark user as having voted
        with database:
            database.execute("INSERT INTO voters (id) VALUES (?)", (str(message.author.id),))
    
    except Exception as e:
        print(e)
        await log(f"Error running /vote.",channel=message.channel)
        await log(f"Error running /vote.")



# async def command_getData(message):
#     if str(message.author.id) != ADMIN:
#         await message.channel.send("You do not have the permissions to use this command")
#         return
#     with database:
#         rows = database.execute("SELECT * FROM tickets LIMIT 10").fetchall()

#     output = ""
#     for row in rows:
#         output += str(row) + "\n"

#     print(output)
#     await message.channel.send(output)



async def command_info(message):
    # await message.channel.send("ERROR: This command is incomplete. Please contact Graydon Bush to rectify this.")
    await message.channel.send("""
We are voting to elect ***7*** moderators.
In the first question in the form you may vote for up to ***5*** people you believe have the qualities a moderator needs (good at conflict resolution, impartial, etc). A vote of confidence.
In the second question in the form you may vote for up to ***2*** people you believe do not have the qualities a moderator needs. A vote of no-confidence.
These ***2*** votes will count as negative votes, so if someone have 5 votes of confidence and 2 votes of no-confidence they will be considered to have 3 total votes.

At the end of the voting period, the 7 people with the highest number of total votes (total votes = # of confidence votes - # of no-confidence votes) will be our moderators.
        """)


async def command_numVotes(message):
    with database:
        rows = database.execute("SELECT used FROM tickets WHERE used=?", (True,)).fetchall()
    await message.channel.send(f"{len(rows)} voting link(s) have been sent.")


async def command_enable(message):
    if str(message.author.id) != ADMIN:
        await message.channel.send("You do not have the permissions to use this command")
        return
    global_settings["enable"] = True
    await message.channel.send("Bot commands enabled")


async def command_disable(message):
    if str(message.author.id) != ADMIN:
        await message.channel.send("You do not have the permissions to use this command")
        return
    global_settings["disable"] = False
    await message.channel.send("Bot commands disabled")


commands = {
    "uploadLinks":{"enable":True, "func":command_uploadLinks}, # ADMIN only
    "uploadAsbesties":{"enable":True, "func":command_uploadAsbesties}, # ADMIN only
    "vote":{"enable":True, "func":command_vote},
    # "getData":{"enable":True, "func":command_getData},       # ADMIN only
    "info":{"enable":True, "func":command_info},
    "numVotes":{"enable":True, "func":command_numVotes},
    "enable":{"enable":True, "func":command_enable},           # ADMIN only
    "disable":{"enable":True, "func":command_disable}          # ADMIN only
    }



#==================Message Handler======================

async def process_commands(message):
    print("Processing commands\n")
    

    done = False
    for command in commands.keys():
        if not done and message.content.startswith(f"/{command}"):
            # if a command was detected but commands are disabled send error message and return
            if global_settings["enable"] == False and str(message.author.id) != ADMIN:
                await message.channel.send("ERROR: Commands disabled")
                return                

            # if commands aren't disabled, try to run command
            try:
                async with message.channel.typing():
                    await commands[command]["func"](message)
                    done = True
            except:
                await log(f"Error running command {command}.",channel=message.channel)
 

#==================-Client Events==================-


@client.event
async def on_message(message):
    if not message.author.bot:
        await process_commands(message)

@client.event
async def on_guild_join(guild):
    print(f"JOINED GUILD {guild.name}")
    await log(f"JOINED GUILD {guild.name}")

@client.event
async def on_ready():
    set_up_log()

    print(f'Logged in as {client.user} (ID: {client.user.id})') # type: ignore

    for guild in client.guilds:
        print(f'Connected to guild: {guild.name} (ID: {guild.id})')

    global database
    database = sqlite3.connect('tickets.db')
    print(f"Connected to database: {database}")

    with database:
        database.execute("CREATE TABLE IF NOT EXISTS tickets (link TEXT PRIMARY KEY, used BOOL NOT NULL)")
        database.execute("CREATE TABLE IF NOT EXISTS voters (id TEXT PRIMARY KEY)")
        database.execute("CREATE TABLE IF NOT EXISTS asbesties (id TEXT PRIMARY KEY)")


    if database == None:
        startup_errors.append(log_format(f"Error connecting to database"))

    print('======\n')

    for e in startup_errors:
            await error_logging_obj.send(e)



client.run(TOKEN)  # type: ignore


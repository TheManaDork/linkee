startup_errors = []
# schedule_errors = []
TOKEN = None

#==================Error Logging Imports====================
import traceback

#==================Settings====================
import settings as _s # annoyed this can't go in Import Files but _s.init() needs to be run before quotes_etc
_s.init()
error_logging_channel = _s.error_logging_channel
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
        out=f':x: ERROR:\n```{traceback.format_exc()}```{channel}{other_info}'
    else:
        out=f':green_circle: LOG:\n```{traceback.format_exc()}```{channel}{other_info}'
    return out

async def log(details="",channel="",level=0,error=True):
    output = log_format(details,channel,level,error)
    print(output)
    await error_logging_obj.send(output)


#==================Import Libs======================

import os, sys, discord, pickle, datetime, random, threading, uuid, time, asyncio
import regex as re
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv


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



#==================Variable Inits==================-
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
_s.ADMIN = str(os.getenv("OPPED_USER"))

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)



#==================Import Files======================
import command_handler
import quotes_etc
import helper
import activityTracker as tracker
import scheduler



#==================Load Sticky Data==================
perma_data = {"reverse_enable":dict,"quote_mutes":list,"all_quotes":list,"user_ids":dict,"tasks":list, "last_message_dates":dict, "quad_alarms": dict, "ignoredUsers":set} #last_message_dates will = dict{user_ids:list(timestamps)}


for v in perma_data.keys():
    try:
        with open(f'pickle_files/{v}.pkl', 'rb') as f:
            perma_data[v] = pickle.load(f)
    except:
        perma_data[v] = perma_data[v]()


#==================Start Stuff W/ Dependencies==================
try:
    scheduler.start()
except:
    startup_errors.append(log_format(f'Error starting scheduler.'))



#==================-Client Events==================-


@client.event
async def on_message(message):
    if not message.author.bot:
        # print(type(message.created_at))
        print(f"{message.created_at:%b-%d, %I:%m %p} [{message.channel}] <{message.author.display_name[:50]}> \"{message.content[:100]}\"")

        try:
            await tracker.trackActivity(message)
        except Exception as e:
            await log("Error calling trackActivity:\n" + str(e))

        await command_handler.process_commands(message)
        await quotes_etc.go(message)

@client.event
async def on_guild_join(guild):
    print(f"JOINED GUILD {guild.name}", flush=True)
    await log(f"JOINED GUILD {guild.name}")

@client.event
async def on_ready():

    set_up_log()

    print(f'Logged in as {client.user} (ID: {client.user.id})') # type: ignore

    for guild in client.guilds:
        print(f'Connected to guild: {guild.name} (ID: {guild.id})')

    # global database
    _s.database = sqlite3.connect('tickets.db')
    print(f"Connected to database: {_s.database}", flush=True)

    with _s.database:
        _s.database.execute("CREATE TABLE IF NOT EXISTS tickets (link TEXT PRIMARY KEY, used BOOL NOT NULL)")
        _s.database.execute("CREATE TABLE IF NOT EXISTS voters (id TEXT PRIMARY KEY)")
        _s.database.execute("CREATE TABLE IF NOT EXISTS asbesties (id TEXT PRIMARY KEY)")

    if _s.database == None:
        startup_errors.append(log_format(f"Error connecting to database"))

    print('======\n', flush=True)

    for e in startup_errors:
            await error_logging_obj.send(e)



client.run(TOKEN)  # type: ignore


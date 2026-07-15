import __main__ as _m
import settings as _s
last_to_talk_in_excuses = False
quotes_channel = _s.quotes_channel


# Notes:
# - There is a bug somewhere in here, restart bot -> daily_quest cancel always cancels 1 more instances of daily_historic_quote than have been scheduled/that daily_quote list sees


async def new_user(user_id, guild): # note: there is a discord.message.clean_content attribute that does some of this - Graydon
    user_ids = _m.perma_data["user_ids"] #this is just a reference, so editing user_ids here changes the one back in _m.perma_data["user_ids"] as well
    try:
        g = 0 if not guild else guild.id
        if g not in user_ids.keys():
            user_ids[g] = {}
        if user_id not in user_ids[g].keys():
            if guild == None:
                user_ids[g][user_id] = _m.client.get_user(user_id).display_name
            else:
                member = await guild.fetch_member(user_id)
                if member.nick == None:
                    user_ids[g][user_id] = _m.client.get_user(user_id).display_name
                else:
                    user_ids[g][user_id] = member.nick
            _m.helper.save_sticky_data("user_ids")
    except:
        await _m.log("Failed to cache new user")

async def clean_at_mentions(text,*extra,**extra2):
    user_ids = _m.perma_data["user_ids"] #this is just a reference, so editing user_ids here changes the one back in _m.perma_data["user_ids"] as well

    guild = _m.client.get_guild(text[1])
    await new_user(text[2], guild)
    if (0 if guild == None else guild.id) in user_ids.keys() and len(text)>=3 and text[2] in user_ids[0 if guild == None else guild.id].keys():
        author = f" [{user_ids[0 if guild == None else guild.id][text[2]]}('s)]"
    else:
        author = ""
             
    text = text[0]         
    try:
        mentions = _m.re.findall(r"<@\d+?>",text)
        for m in mentions:
            await new_user(int(m[2:-1]), guild)
            if (0 if guild == None else guild.id) in user_ids.keys() and int(m[2:-1]) in user_ids[0 if guild == None else guild.id].keys():
                text = str(text.replace(m,user_ids[0 if guild == None else guild.id][int(m[2:-1])]))
                
                
        if (any([x in text.lower() for x in ["i'","me","my","mine"]]) or "I" in text) and len(text)<500:
            MEs=[m.end(0) for m in _m.re.finditer(r"([“”’'\"‘—-][^“”’'\"‘—\-\n\r]*?[\n\r]?[^“”’'\"‘—\-\n\r]*?){2}(?!.*[“”’'\"‘].*)([“”’‘' \"^—\-\n\r]|^)(i['‘’][a-z]+|(i|me|my|mine)(?=[' “‘”’\".,?!\n\r]|$))", text, _m.re.IGNORECASE)]
            print(MEs,author)
            offset = 0
            for me in MEs:
                text = text[:me+offset]+author+text[me+offset:]
                offset+=len(author)
        return str(text)
    except Exception as e:
        await _m.log()

async def update_quotes(message,*extra,**extra2):
    i=0
    try:
        # if message.content.startswith("a!get_all_quotes"):
        _m.perma_data["all_quotes"] = []
        await message.channel.typing()
        try:
            async for msg in _m.client.get_channel(quotes_channel).history(limit = 20000):
                if any([x in msg.content for x in '“"”']):
                    i+=1
                    _m.perma_data["all_quotes"].append((msg.content,msg.guild.id,msg.author.id))
                    if i%100==0:
                        await message.reply(f"...got {i} quotes so far...")
                        await message.channel.typing()
        except:
            await _m.log(f"couldn't access channel {quotes_channel} to get quotes", error=False)

        _m.perma_data["all_quotes"] = list(set(_m.perma_data["all_quotes"]))
        _m.helper.save_sticky_data("all_quotes")

        await message.reply("Done! There are now {} quotes in the cache.".format(len(_m.perma_data["all_quotes"])))
    except Exception as e:
        await _m.log(channel=message.channel)

async def add_quote(message,*extra,**extra2):
    all_quotes = _m.perma_data["all_quotes"] #this is just a reference, so editing all_quotes here changes the one back in _m.perma_data["all_quotes"] as well
    
    try:
        if message.channel.id in [quotes_channel] and any([x in message.content for x in '“"”']):
            all_quotes.append((message.content,message.guild.id,message.author.id))
            _m.helper.save_sticky_data("all_quotes")
    except Exception as e:
        await _m.log(channel=message.channel)

async def update_user_ids(message,*extra,**extra2):
    # if message.content.startswith("a!new_user_ids"):
    _m.perma_data["user_ids"] = dict()
    _m.helper.save_sticky_data("user_ids")
    await message.channel.send("Done!")

async def quote_mute(message,*extra,**extra2):
    global last_to_talk_in_excuses
    try:
        if message.channel.id == quotes_channel or message.channel.id == 1335680124213006337:
            _m.perma_data["quote_mutes"] = [m for m in _m.perma_data["quote_mutes"] if not _m.helper.is_five_minutes_past(m[1])]

            if message.author.id in [i[0] for i in _m.perma_data["quote_mutes"]] and len(_m.re.findall("[“”’'\"‘].+[“”’'\"‘](.|\\n)*(?!<@"+str(message.author.id)+">)<@(\\d{17,21})>",message.content))==0:
                if message.author.id != last_to_talk_in_excuses:
                    last_to_talk_in_excuses = message.author.id
                    await _m.client.get_channel(1307445812367851630).send("<@{}> just tried to send the following message in quotes (but it's probably just a somewhat invalid excuse as they were [just quoted]({})).\n\"{}\"".format(message.author.id,_m.perma_data["quote_mutes"][[i[0] for i in _m.perma_data["quote_mutes"]].index(message.author.id)][2],message.content))
                else:
                    await _m.client.get_channel(1307445812367851630).send("\"{}\"".format(message.content))
                    
                await message.delete()
            else:
                mentions = _m.re.findall("<@(\d{17,21})>",message.content)
                _m.perma_data["quote_mutes"] += [[int(x),_m.datetime.datetime.utcnow(),message.jump_url] for x in set(mentions)]
            
            _m.helper.save_sticky_data("quote_mutes")
                
        elif message.channel.id == 1307445812367851630 and message.author.id != 1279137176814354586:
            pass#await message.delete()
    except Exception as e:
        await _m.log(channel=message.channel)
        
        
async def quote_from_sched(channel_id):
    print("Quoting from schedule")
    c = _m.client.get_channel(channel_id)
    if channel_id != quotes_channel:
        quotes = list()
        await c.typing()
        quotes += _m.perma_data["all_quotes"]
        quote_message = await _m.quotes_etc.clean_at_mentions(_m.random.choice(quotes))
        await c.send(quote_message)
    #await c.send("[quote here]")
    print(_m.perma_data["tasks"])

    today = _m.datetime.datetime.today()
    new_timestamp =  (_m.datetime.datetime(today.year, today.month, today.day, 8, 0)+_m.datetime.timedelta(days=1)).timestamp()
    _m.scheduler.new_task_no_lock(new_timestamp,"daily_quote",args=[channel_id])
    print(_m.perma_data["tasks"])


async def daily_quote_commands(message):
    # if message.content.lower().startswith("a!daily_quote"):
    if message.channel.id != quotes_channel:
        message_items = message.content.lower().split(" ")
        if message_items[1] == "new":
            today = _m.datetime.datetime.today()
            new_timestamp =  _m.datetime.datetime(today.year, today.month, today.day, 8, 0).timestamp()
            # new_timestamp = (_m.datetime.datetime.today() + _m.datetime.timedelta(minutes=2)).timestamp()
            _m.scheduler.new_task(new_timestamp,"daily_quote",args=[message.channel.id])
            await message.channel.send("Quotes will be sent to this channel daily starting 8:00am today (or right now, if you slept in).\nUse `a!daily_quote cancel` to stop.")
        
        elif message_items[1] == "list":
            _m.scheduler.l.acquire()
            x=[]
            for i in range(len(_m.perma_data["tasks"])):
                if _m.perma_data["tasks"][i][1]=="daily_quote" and _m.perma_data["tasks"][i][4][0]==message.channel.id:
                    x.append(_m.perma_data["tasks"][i])
            _m.helper.save_sticky_data("tasks")
            _m.scheduler.l.release()
            await message.channel.send(f"Found {len(x)} instances of daily_quote for this channel:\n```"+"\n".join([f"Next timestamp: "+str(y[0]) for y in x])+"```")
        
        elif message_items[1] == "cancel":
            _m.scheduler.l.acquire()
            x=0
            i=0
            while i<len(_m.perma_data["tasks"]):
                if _m.perma_data["tasks"][i][1]=="daily_quote" and _m.perma_data["tasks"][i][4][0]==message.channel.id:
                    #print(f"del {i}")
                    del _m.perma_data["tasks"][i]
                    x+=1
                    i-=1
                i+=1
            _m.helper.save_sticky_data("tasks")
            _m.scheduler.l.release()
            await message.channel.send(f"Deleted {x} instances of daily_quote for this channel")
        elif message_items[1] == "help":
            await message.channel.send("`a!daily_quote list` to list current instances of daily_quote task for this channel\n`a!daily_quote cancel` to to sending daily quotes to this channel\n`a!daily_quote new` to add a new instance of the dail_quotes task for this channel (start sending quotes here)")
    else: 
        await message.channel.send("<:error:1282747613413638305> no a!quote-ing in a quote channel!! <:error:1282747613413638305>")
            
            
async def leaderboard(message):
    # if message.content.startswith("a!leaderboard"):
    await message.channel.typing()
    items = message.content.split(" ")
    leader_emojis = ":first_place: :second_place: :third_place: :four: :five: :six: :seven: :eight: :nine:".split(" ")
    leaderboard = [[m.id,_m.helper.count_user_quotes(m.id)] for m in _m.client.get_guild(1277433994459353159).members]
    leaderboard.sort(key=lambda x: x[1],reverse=True)
    estart=0
    if len(items) == 1:
        #print full top 10
        output=["Quotes Leaderboard:"]  
        leaderboard = leaderboard[:9]
    else:
        target = _m.re.findall("(\d{17,21})",items[1])
        if len(target)<1:
            await message.channel.send("Couldn't find user id. Usage: `a!leaderboard` - (top 9) `a!leaderboard <user_id or @ mention>` - specific user.")
            return
        target = int(target[0])
        output = [f"Quotes Leaderboard for <@{target}>:"]
        for i,cont in enumerate(leaderboard):
            if cont[0] == target:
                index = i
                break
        leaderboard = leaderboard[max(0,index-4):min(len(leaderboard),index+5)]
        estart=max(0,index-4)
            
    for i, (u, c) in enumerate(leaderboard, estart):
        #print(f"{leader_emojis[i] if i<5 else _m.helper.to_emoji_num(i)} - <@{u}>: {int(c)}")
        #print(len(str(estart+len(leaderboard))),len(str(estart+(i))),estart,i)
        output.append(f"{('   '*(len(str(estart+len(leaderboard)))-len(str(i+1))))+(leader_emojis[i] if i<5 else _m.helper.to_emoji_num(i))} - <@{u}>: {c}")#passing my user id because the function needs one, but won't use it in this case
    output = [await clean_at_mentions((o,1277433994459353159,669636731284226051)) for o in output]
    output[0] = "**__"+output[0].center(int(1.17*max([len(x) for x in output])))+"__**"
    await message.channel.send("\n".join(output))
        
async def author_leaderboard(message):
    # if message.content.startswith("a!author_leaderboard") or message.content.startswith("a!aleaderboard"):
    await message.channel.typing()
    items = message.content.split(" ")
    leader_emojis = ":first_place: :second_place: :third_place: :four: :five: :six: :seven: :eight: :nine:".split(" ")
    leaderboard = [[m.id,_m.helper.count_user_authoring(m.id)] for m in _m.client.get_guild(1277433994459353159).members]
    leaderboard.sort(key=lambda x: x[1],reverse=True)
    estart=0
    if len(items) == 1:
        #print full top 10
        output=["Quoters Leaderboard:"]  
        leaderboard = leaderboard[:9]
    else:
        target = _m.re.findall("(\d{17,21})",items[1])
        if len(target)<1:
            await message.channel.send("Couldn't find user id. Usage: `a!aleaderboard` or `a!author_leaderboard` - (top 9) `a!aleaderboard <user_id or @ mention>` or `a!author_leaderboard <user_id or @ mention>` - specific user.")
            return
        target = int(target[0])
        output = [f"Quoters Leaderboard for <@{target}>:"]
        for i,cont in enumerate(leaderboard):
            if cont[0] == target:
                index = i
                break
        leaderboard = leaderboard[max(0,index-4):min(len(leaderboard),index+5)]
        estart=max(0,index-4)
            
    for i, (u, c) in enumerate(leaderboard, estart):
        #print(f"{leader_emojis[i] if i<5 else _m.helper.to_emoji_num(i)} - <@{u}>: {int(c)}")
        #print(len(str(estart+len(leaderboard))),len(str(estart+(i))),estart,i)
        output.append(f"{('   '*(len(str(estart+len(leaderboard)))-len(str(i+1))))+(leader_emojis[i] if i<5 else _m.helper.to_emoji_num(i))} - <@{u}>: {c}")#passing my user id because the function needs one, but won't use it in this case
    output = [await clean_at_mentions((o,1277433994459353159,669636731284226051)) for o in output]
    output[0] = "**__"+output[0].center(int(1.17*max([len(x) for x in output])))+"__**"
    await message.channel.send("\n".join(output))
        
        
async def go(message):
    # methods = [quote_mute, update_quotes, add_quote, update_user_ids, daily_quote_commands, leaderboard, author_leaderboard]#,reverse_all]

    # methods only run by commands:
    # - update_user_ids (a!new_user_ids)
    # - daily_quote_commands (a!daily_quote)
    # - leaderboard (a!leaderboard)
    # - author_leaderboard (a!aleaderboard)
    # - update_quotes (a!get_all_quotes)

    # for m in methods:
        # try:
            # await m(message)
        # except:
            # await _m.log()
    pass
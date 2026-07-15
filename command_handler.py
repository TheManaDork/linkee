import __main__ as _m
import settings as _s
import quotes_etc as _q

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


#==================Voting Commands======================


async def command_sayHi(message):
    print("sayHi", flush=True)
    await message.channel.send("Saying hi! From Graydon's computer!")
    print("Someone said hi! I'm alive!", flush=True)   


async def command_uploadLinks(message):
    print("uploadLinks", flush=True)
    if str(message.author.id) != _s.ADMIN:
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

    try:
        with _s.database:
            for link in links:
                _s.database.execute("INSERT INTO tickets (link, used) VALUES (?,?)", (link, False))
    except:
        await message.channel.send("A problem occured while uploading links.")

    print(f"Added {len(links)} links to tickets", flush=True)
    await message.channel.send(f"Added {len(links)} links!")


async def command_uploadVoters(message):
    print("uploadVoters", flush=True)

    if str(message.author.id) != _s.ADMIN:
        await message.channel.send("You do not have the permissions to use this command")
        return

    if len(message.attachments) != 1:
        await message.channel.send("Command must be sent with one attachment")
        return
    r = requests.get(message.attachments[0].url)
    IDs = r.text.split('\n')
    IDs = [ID.strip() for ID in IDs if ID.strip()]

    with _s.database:
        for ID in IDs:
            if not ID.isnumeric():
                print(ID)
                continue
            _s.database.execute("INSERT INTO asbesties (id) VALUES (?)", (ID,))

    print(f"Added {len(IDs)} IDs!", flush=True)
    await message.channel.send(f"Added {len(IDs)} IDs!")


async def command_vote(message):
    print("vote", flush=True)
    try:
        # check environment
        if isinstance(message.author, discord.User):
            print("Is private!", flush=True)
        else:
            print("WARNING: Is public", flush=True)
            await message.channel.send("ERROR: Command can only be used in DM's.")
            return

        # check user is an asbestie
        output = _s.database.execute("SELECT id FROM asbesties WHERE id=?", (str(message.author.id),)).fetchall()

        if len(output) < 1:
            await message.channel.send("""
You must be a member of the Asbestos Pool Swimming Club in order to vote. 
If you are a member of the Asbestos Pool Swimming Club, please reach out to the organizers of this election.
                """)
            return

        # check user has not voted before
        output = _s.database.execute("SELECT id FROM voters WHERE id=?", (str(message.author.id),)).fetchall()

       
        if len(output) > 0:
            await message.channel.send(""" 
You have already received your voting link. You cannot get another one. If you were unable to vote with the link you were given or if this is the first time you have requested a link, please contact Graydon Bush, username TheManaDorh
                """)
            return

        # retrieve voting link and mark link as used
        output = _s.database.execute("UPDATE tickets SET used = TRUE WHERE link = (SELECT link FROM tickets WHERE used = FALSE LIMIT 1) RETURNING link;").fetchone()

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
        with _s.database:
            _s.database.execute("INSERT INTO voters (id) VALUES (?)", (str(message.author.id),))
    
    except Exception as e:
        print(e, flush=True)
        await log(f"Error running /vote.",channel=message.channel)
        await log(f"Error running /vote.")



async def command_info(message):
    print("info", flush=True)
    # await message.channel.send("ERROR: This command is incomplete. Please contact Graydon Bush to rectify this.")
    await message.channel.send("""
We are voting to elect ***7*** moderators.
In the first question in the form you may vote for up to ***5*** people you believe have the qualities a moderator needs (good at conflict resolution, impartial, etc). A vote of confidence.
In the second question in the form you may vote for up to ***2*** people you believe do not have the qualities a moderator needs. A vote of no-confidence.
These ***2*** votes will count as negative votes, so if someone have 5 votes of confidence and 2 votes of no-confidence they will be considered to have 3 total votes.

At the end of the voting period, the 7 people with the highest number of total votes (total votes = # of confidence votes - # of no-confidence votes) will be our moderators.
        """)


async def command_introduce(message):
    print("introduce", flush=True)
    await message.channel.send("""
Hello! My name's Linkee, and I'm a voting bot!
To vote in this election please DM me the command '/vote' and I'll send you a single-use link you can use to vote!
You can click the link multiple times, to be clear, but via that link you can only fill out the voting form once.
And I'll only ever send you one link so please try to make good use of it!

Hearts <3,
Linkee
Code.org, May '22
        """)


async def command_numVotes(message):
    print("numVotes", flush=True)
    print(_s.database)
    with _s.database:
        rows = _s.database.execute("SELECT used FROM tickets WHERE used=?", (True,)).fetchall()
    await message.channel.send(f"{len(rows)} voting link(s) have been sent.")


async def command_enable(message):
    print("enable", flush=True)
    if str(message.author.id) != _s.ADMIN:
        await message.channel.send("You do not have the permissions to use this command")
        return
    _s.settings["enable"] = True
    await message.channel.send("Bot commands enabled")


async def command_disable(message):
    print("disable", flush=True)
    if str(message.author.id) != _s.ADMIN:
        await message.channel.send("You do not have the permissions to use this command")
        return
    _s.settings["disable"] = False
    await message.channel.send("Bot commands disabled")

async def command_checkAdmin(message):
    if _s.ADMIN in [member.id for member in message.guild.members]:
        await message.channel.send(f"<@{_s.ADMIN}> is admin")
        print("Admin found")
    else:
        await message.channel.send("No Admin found")
        print("No admin found")



#==================Quote Commands======================


async def command_quote(message):
    if message.channel.id != _s.quotes_channel:
        quotes = list()
        await message.channel.typing()
        quotes += _m.perma_data["all_quotes"]
        quote_message = await _m.quotes_etc.clean_at_mentions(_m.random.choice(quotes))
        await message.channel.send(quote_message)
    else: 
        await message.channel.send("<:error:1282747613413638305> no a!quote-ing in a quote channel!! <:error:1282747613413638305>")


async def command_new_user_ids(message):
    await _q.update_user_ids(message)


async def command_daily_quote(message):
    await _q.daily_quote_commands(message)


async def command_leaderboard(message):
    await _q.leaderboard(message)


async def command_aleaderboard(message):
    await _q.author_leaderboard(message)


async def command_get_all_quotes(message):
    await _q.update_quotes(message)


async def command_search(message):
    print("search")
    # Discord maximum message length
    DISCORD_MAX_LENGTH = 2000
    # A safe limit for a single message to account for separators and potential prefix/suffix
    SAFE_MSG_LIMIT = 1990 
    
    if message.channel.id != _s.quotes_channel:
        print("searching...")
        target = message.content.split(" ")
        if len(target) < 2:
            await message.channel.send("Not enough arguments")
            return
        
        # Determine the total character limit for the search results (based on original logic)
        l = target[0].split("_")  # Define l before using it
        limit = int(l[1]) if len(l) > 1 else DISCORD_MAX_LENGTH - 30
                
        async with message.channel.typing():
            # Make the search case-insensitive: lowercase the search token once
            search_token = target[1].lower()

            # List to store all full quotes that match the search criteria
            # We will collect every matching quote (no overall cutoff) and pack them into blocks
            targetQuotes = []

            # Now iterate persistent quotes and collect the cleaned full quote text
            for q, g, a in _m.perma_data["all_quotes"]:
                # q is the raw quote text; match case-insensitively but preserve original q in output
                if search_token in q.lower():
                    q_clean = await _m.quotes_etc.clean_at_mentions((q, g, a))
                    q_clean_formatted = _m.re.sub("\n\n+", "\n", q_clean)
                    if not q_clean_formatted:
                        continue
                    targetQuotes.append(q_clean_formatted)

            if not targetQuotes:
                await message.channel.send("That search returned no results")
                return

            # 2. PACK FULL QUOTES INTO MESSAGE-BLOCKS
            # Use a double-newline between quotes to preserve separation
            targetMessages = []
            current_message_content = ""
            current_message_length = 0

            for quote_text in targetQuotes:
                separator = "\n\n"
                quote_len_with_sep = len(quote_text) + (len(separator) if current_message_content else 0)

                if current_message_length + quote_len_with_sep > SAFE_MSG_LIMIT:
                    if current_message_content:
                        targetMessages.append(current_message_content)
                    current_message_content = quote_text
                    current_message_length = len(quote_text)
                else:
                    current_message_content += (separator if current_message_content else "") + quote_text
                    current_message_length += quote_len_with_sep

            if current_message_content:
                targetMessages.append(current_message_content)

            # 3. SEND EACH BLOCK INDIVIDUALLY
            # Use DISCORD_MAX_LENGTH for final safety (2000 chars)
            for i in range(len(targetMessages)):
                block = targetMessages[i]

                if len(block) <= DISCORD_MAX_LENGTH:
                    await message.channel.send(block)
                else:
                    # Split by lines preserving line breaks where possible
                    lines = block.splitlines(True)
                    sub_chunks = []
                    cur = ""
                    for line in lines:
                        if len(cur) + len(line) > DISCORD_MAX_LENGTH:
                            if cur:
                                sub_chunks.append(cur)
                                cur = line
                            else:
                                # single line exceeds limit; hard-split the line
                                start = 0
                                while start < len(line):
                                    slice = line[start:start+DISCORD_MAX_LENGTH]
                                    sub_chunks.append(slice)
                                    start += DISCORD_MAX_LENGTH
                                cur = ""
                        else:
                            cur += line
                    if cur:
                        sub_chunks.append(cur)

                    for sc in sub_chunks:
                        await message.channel.send(sc)

            print(targetMessages)


async def command_activityTracker(message):
    message_split = message.content.split(" ")
    print(str(_s.ADMIN) +" == " + str(message.author.id))
    if message.author.id != _s.ADMIN:
        await message.channel.send("ERROR: Invalid perms")
        return

    if len(message_split) > 1: # await _m.helper.hasPerms("Daddy", message.author):
        print("Running activityTracker")
        # initialize a new local instance of activity check scheduling
        if message_split[1] == "schedule":
                await _m.tracker.init_check_from_sched(message)
        
        # print all local instances of activity check scheduling
        elif message_split[1] == "get":
            output = ""
            # await message.channel.send("Getting tasks")
            for task in _m.perma_data["tasks"]:
                if task[1] == "daily_activity_check":
                    output += str(task)+ "\n\n"
            if len(output) > 0:
                await message.channel.send(output)            
            else:
                await message.channel.send("No instances of 'daily_activity_check' found")
            

        # manually run activity check...
        elif message_split[1] == "check":
            # ...on all users
            if len(message_split) > 2 and message_split[2] == "all" and message.author.id == _s.ADMIN: # await _m.helper.hasPerms("Daddy", message.author):
                await _m.tracker.check_manually(message)

            # ... on a specific user ...
            else:
                name = ""
                if len(message_split) > 2: 
                    name = message_split[2]
                    if isinstance(name, str) and name[0] == '<': # ... given by @username format
                        name = name[2:-1]
                else:
                    name = message.author.id
                
                try: 
                    name = int(name)
                except:
                    await message.channel.send("ERROR: Invalid name provided")
                    return

                print("user id = ", str(name))
                # run activity check on given user
                if _m.tracker.checkUserActivity(message, name):
                    await message.channel.send(_m.client.get_user(name).display_name+" gets perms!")
                    await _m.tracker.setActive(message, name)
                else:
                    await message.channel.send(_m.client.get_user(name).display_name+" doesn't get perms. :(")
                    await _m.tracker.setInactive(message, name)

        # cancel all local instances of activity check scheduling
        elif message_split[1] == "cancel": # deletes the first instance of activity check scheduling
            if len(message_split) <= 2:    
                i = 0
                while i < len(_m.perma_data["tasks"]):
                    if _m.perma_data["tasks"][i][1] == "daily_activity_check":
                        del _m.perma_data["tasks"][i]
                        _m.helper.save_sticky_data("tasks")
                        await message.channel.send("Deleted an instance of 'daily_activity_check'")
                        return
                    i += 1
                await message.channel.send("No instances of 'daily_activity_check' found")
            elif len(message_split) > 2 and message_split[2] == "all":
                instances = 0
                i = 0
                while i < len(_m.perma_data["tasks"]):
                    if _m.perma_data["tasks"][i][1] == "daily_activity_check":
                        del _m.perma_data["tasks"][i]
                        instances+=1
                        i -= 1
                    i+=1
                await message.channel.send(f"Canceled {instances} instances of daily_activity_check")
                _m.helper.save_sticky_data("tasks")
        else:
            await message.channel.send("ERROR: Invalid command and/or syntax")
    else:
        await message.channel.send("ERROR: Invalid command/syntax")


async def command_messageHistory(message):
    message_split = message.content.split(" ")
    if len(message_split) > 1:
        
        # print a user's message history
        if message_split[1] == "get": 
            # await message.channel.send("Searching message history")

            # if user was specified...
            if len(message_split) > 2:
                name = message_split[2]

                # ...by the format @username:
                if name[0] == '<': 
                    name = name[2:-1] 
                    try:
                        name = int(name)
                    except:
                        pass

                # ...ids: sends all stored ids
                elif name == "ids":
                    Id_list = []
                    for Id in _m.perma_data["last_message_dates"]:
                        Id_list.append(Id)
                    output = str(len(_m.perma_data["last_message_dates"]))+" ids:\n" + str(Id_list)
                    await _m.helper.sendLargeOutput(message, output, True)
                    return

                # ...names: sends each ids' corresponding display names 
                elif name == "names":
                    name_list = []
                    member_ratio = 0
                    for member in message.guild.members:
                        if member.id in _m.perma_data["last_message_dates"]:
                            name_list.append(member.display_name+"\n")
                            member_ratio += 1

                    output = (str(member_ratio)+"/"+str(len(message.guild.members))+
                             " members accounted for:\n"+
                             ' '.join(name_list))
                    await _m.helper.sendLargeOutput(message, output, True)
                    return
                # ...via user id
                else: 
                    try:
                        name = int(name)
                    except:
                        await message.channel.send("Failed to convert name to ID")
                        return

                # find and send specified user's message history
                if name in _m.perma_data["last_message_dates"]: 
                    await message.channel.send("\# of messages stored: " + str(len(_m.perma_data["last_message_dates"][name])) + "\n" + str([_m.datetime.fromisoformat(d).strftime("%x @ %I:%M %p") for d in _m.perma_data["last_message_dates"][name]]))
                else:
                    await message.channel.send("userId " + str(name) + " is not recognized")
                    return
                    
            else: # if no user was specified, return messageHistory for the person who sent the command
                await message.channel.send("\# of messages stored: " + str(len(_m.perma_data["last_message_dates"][message.author.id])) + "\n" +str(_m.perma_data["last_message_dates"][message.author.id]))
            return

        # Graydon only commands. Do irreversible things to the messageHistory data
        elif message.author.id == _s.ADMIN:

            # clears info in last_message_dates
            if message_split[1] == "clear":
                if message_split[2] == "all":
                    _m.perma_data["last_message_dates"] = []
                    await message.channel.send("all message dates deleted. Hope you meant to do that!")
                else:
                    await message.channel.send("Currently can only clear all")
                return

            # remove invalid user ids from last_message_dates db
            elif message_split[1] == "clean":
                types = set()
                badKeys = set()
                for key in list(_m.perma_data["last_message_dates"]):
                    types.add(type(key))

                    if not isinstance(key, int):
                        badKeys.add(key)
                        _m.perma_data["last_message_dates"].pop(key)
                    else:
                        member = message.guild.get_member(key)
                        if member is None:
                            badKeys.add(key)
                            _m.perma_data["last_message_dates"].pop(key) 
                        elif  member.joined_at is None:
                            badKeys.add(key)
                            _m.perma_data["last_message_dates"].pop(key)                   

                _m.helper.save_sticky_data("last_message_dates")
                await message.channel.send(types)
                await message.channel.send("Removed "+str(len(badKeys))+" keys")
            else:
                await message.channel.send("ERROR: Invalid command syntax")
        else:
            await message.channel.send("ERROR: Invalid command syntax")


commands = {
# Voting Commands
    "uploadLinks":{"enable":True, "func":command_uploadLinks}, # ADMIN only
    "uploadVoters":{"enable":True, "func":command_uploadVoters}, # ADMIN only
    "vote":{"enable":True, "func":command_vote},
    # "getData":{"enable":True, "func":command_getData},       # ADMIN only
    "info":{"enable":True, "func":command_info},
    "introduce":{"enable":True, "func":command_introduce},
    "numVotes":{"enable":True, "func":command_numVotes},
# Misc Commands
    "sayHi":{"enable":True, "func":command_sayHi},
    "enable":{"enable":True, "func":command_enable},           # ADMIN only
    "disable":{"enable":True, "func":command_disable},          # ADMIN only
    "checkAdmin":{"enable":True, "func":command_checkAdmin},
# Quote Commands
    "quote":{"enable":True, "func":command_quote},
    "new_user_ids":{"enable":True, "func":command_new_user_ids},
    "daily_historic_quote":{"enable":True, "func":command_daily_quote},
    "leaderboard":{"enable":True, "func":command_leaderboard},
    "aleaderboard":{"enable":True, "func":command_aleaderboard},
    "get_all_quotes":{"enable":True, "func":command_get_all_quotes},
    "search":{"enable":True, "func":command_search},
# Activity Tracker Commands
    "activityTracker":{"enable":True, "func":command_activityTracker},
    "messageHistory":{"enable":True, "func":command_messageHistory}

    }



async def process_commands(message):
    print("Processing commands\n", flush=True)
    done = False
    for command in commands.keys():
        if not done and message.content.startswith(f"/{command}"):
            # if a command was detected but commands are disabled send error message and return
            if _s.settings["enable"] == False and str(message.author.id) != _s.ADMIN:
                await message.channel.send("ERROR: Commands disabled")
                return                

            # if commands aren't disabled, try to run command
            try:
                async with message.channel.typing():
                    await commands[command]["func"](message)
                    done = True
            except:
                await _m.log(f"Error running command {command}.",channel=message.channel)
 

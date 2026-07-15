import __main__ as _m
import settings as _s
from datetime import datetime, timezone, timedelta

#-------------------- global variables ------------------------

activeId = 1416664166365790359
activeRole = None # _m.discord.Role
inactiveId = 1416664311815868518
inactiveRole = None # _m.discord.Role

#-------------------- activity helper functions ------------------------

def getMessageHistory(name):
    if name in _m.perma_data["last_message_dates"]: 
        return _m.perma_data["last_message_dates"][name]
    print(f"ERROR: {name} is not in last_message_dates")
    return {0, 0}

def isUserInServer(message, user_id, remove=False):
    # if a user id was given
    user_list = [member for member in message.guild.members if member.id == user_id][0]
    if len(user_list) == 1:
        return True

    elif len(user_list) == 0:
        if remove:
            _m.perma_data["last_message_dates"].pop(user_id)
            _m.helper.save_sticky_data("last_message_dates")
        return False

    else:
        print("ERROR: Multiple members have the same member id")


#-------------------- activity functions -------------------------

async def check_from_sched(messageId, channelId, guildId, client=None):
    guild = _m.client.get_guild(guildId)
    message = await guild.get_channel(channelId).fetch_message(messageId)
    today = _m.datetime.datetime.today()
    new_timestamp =  (_m.datetime.datetime(today.year, today.month, today.day, 8, 0)+_m.datetime.timedelta(days=1)).timestamp()    
    _m.scheduler.new_task_no_lock(new_timestamp,"daily_activity_check",args=[messageId, channelId, guildId])
    # run through last_message_dates, add/remove perms.
    await check_manually(message)
    return


async def init_check_from_sched(message, client=None):
    if not _m.helper.message_in_asbestos(message):
        await message.channel.send("ERROR: Command is only valid in the Asbestos Pool Swimming Club")
        return
    await check_from_sched(message.id, message.channel.id, message.guild.id)


async def check_manually(message, client=None):
    if not _m.helper.message_in_asbestos(message):
        await message.channel.send("ERROR: Command is only valid in the Asbestos Pool Swimming Club")
        return
    # run through last_message_dates, add/remove perms.
    activeMembers = ""
    numActiveMembers = 0
    botMembers = ""
    numBotMembers = 0
    inactiveMembers = ""
    numInactiveMembers = 0
    ghostMembers = ""
    numGhosts = 0
    memberDict = {}
    for member in message.guild.members:
        mH = getMessageHistory(member.id)
        if not mH == {0, 0}:
            pass
            # continue
        print(f"{member} == {mH}\n")
        memberDict[member] = getMessageHistory(member.id)

    for member, memberHistory in memberDict.items():
        # print("a member is being judged")
        result = checkUserActivity(message, member, memberHistory)
        if result == -1: # inactive, too few messages
            numInactiveMembers += 1
            print(str(member.display_name)+" is inactive. <10 msg "+str(member.id))
            inactiveMembers += str(await setMemberInactive(message, member)) + " - <10 msgs\n"
        elif result == -2: # inactive, too young
            numInactiveMembers += 1
            print(str(member.display_name)+" is inactive. mH[0]<time(30days) "+str(member.id))
            inactiveMembers += str(await setMemberInactive(message, member)) + " - mH[0]<time(30days)\n"
        elif result == -3: # inactive, insufficient recent activity
            numInactiveMembers += 1
            print(str(member.display_name)+" is inactive. mH[1]>time(4weeks) "+str(member.id))
            inactiveMembers += str(await setMemberInactive(message, member)) + " - mH[1]>time(4weeks)\n"
        elif result == -4: # no history == ghost/lurker
            print(str(member.display_name)+" is inactive. 0 messages "+str(member.id))
            ghostMembers += str(await setMemberInactive(message, member)) + " - 0 msgs\n"
            numGhosts+=1
        elif result == 2: # active, bot
            print(str(member.display_name)+" is a active. A bot")
            botMembers += str(await setMemberActive(message, member)) + " - bot\n"
            numBotMembers += 1
        elif result: # active!
            numActiveMembers += 1
            print(str(member.display_name)+" is active. "+str(member.id))
            activeMembers += str(await setMemberActive(message, member)) + "\n"
        else: # idk, just in case lmao
            numInactiveMembers += 1
            print(str(key)+" is inactive. "+str(len(member)))
            inactiveMembers += str(await setMemberInactive(message, member)) + "\n"
    print("printing results")
    output = ("### ***Active:***\n"+activeMembers+
                "\n### ***Inactive:***\n"+inactiveMembers+
                "\n### ***Bots:***\n"+botMembers+
                "\n### ***Lurkers***\n"+ghostMembers+
                "\nActivity check! We have " + str(numActiveMembers) +
                " active members, " + str(numInactiveMembers) +
                " inactive members, " + str(numBotMembers) +
                " bots, and " + str(numGhosts) +
                " lurkers! (" + str(numActiveMembers+numBotMembers+numInactiveMembers+numGhosts) + "/" + str(len(message.guild.members)) + ")")
    await _m.helper.sendLargeOutput(message, output, True)
    # await _m.helper.sendLargeOutput(message, "### ***Active:***\n"+activeMembers, True)
    # if len(activeMembers) > 2000:
    #     await message.channel.send("### ***Active:***\n"+activeMembers[:1970]+"\n(and more)...")
    # else:
    #     await message.channel.send("### ***Active:***\n"+activeMembers[:2000])
    # await _m.helper.sendLargeOutput(message, "### ***Inactive:***\n"+inactiveMembers, True)
    # if len(inactiveMembers) > 2000:
    #     await message.channel.send("### ***Inactive:***\n"+inactiveMembers[:1968]+"\n(and more)...")
    # else:
    #     await message.channel.send("### ***Inactive:***\n"+inactiveMembers[:2000])
    # await message.channel.send("Manual activity check! We have " + str(numActiveMembers) + " active members and " + str(numInactiveMembers) + " inactive members!")

    return


async def trackActivity(message, client=None):
    if not _m.helper.message_in_asbestos(message):
        return
    # role = _m.discord.utils.get(message.guild.roles, name="graydon comma specifically")
    # if role in message.author.roles: 
        # return

    memberId = message.author.id
    if memberId not in _m.perma_data["last_message_dates"]:
        _m.perma_data["last_message_dates"][memberId] = []

    while len(_m.perma_data["last_message_dates"][memberId]) > 10:
        _m.perma_data["last_message_dates"][memberId].pop(1);

    if len(_m.perma_data["last_message_dates"][memberId]) == 10:
        _m.perma_data["last_message_dates"][memberId].pop(1);
    _m.perma_data["last_message_dates"][memberId].append(message.created_at.isoformat())
    _m.helper.save_sticky_data("last_message_dates")
    print("activityTracker: Message recorded")
    return


def checkUserActivity(message, member, memberHistory={0}):
    if not _m.helper.message_in_asbestos(message):
        print("ERROR: checkActivity: run outside of asbestos")
        return
    if isinstance(member, int) and memberHistory == {0}:
        member = message.guild.get_member(member)
        memberHistory = getMessageHistory(member.id)
    print("Running checkUserActivity")
    if member is None or member.joined_at is None or memberHistory == {0, 0}:
        print(f"{member.id} is not in the guild")
        # return "X - !in guild"
        return -4

    # anyone with the bot role will always be marked active
    if member.bot:
        print("checkActivity: User is a bot")
        # return "Y - bot"
        return 2
    # 3 requirements:
    #1. 10 msgs in msg history:
    #2. msg[0] (the oldest ever) must be 30 days old:
    #3. msg[1] (second oldest) must be less than 4 weeks old
    # print(len(_m.perma_data["last_message_dates"][memberId]))

    # 1.
    if len(memberHistory) < 10:
        print("checkActivity: ", member.display_name, "has too few messages")
        # return "X - <10 mesg"
        return -1
        
    oldestMessageDiff = (datetime.now(timezone.utc) - datetime.fromisoformat(memberHistory[0]))
    secondOldestMessageDiff = (datetime.now(timezone.utc) - datetime.fromisoformat(memberHistory[1]))
    # await message.channel.send("1st diff: " + str(oldestMessageDiff) + "\n2nd diff: " + str(secondOldestMessageDiff) + "\nsize: " + str(len(_m.perma_data["last_message_dates"][memberId])))
    # print(str(oldestMessageDiff) +"\n"+ str(secondOldestMessageDiff))

    # 2.
    if oldestMessageDiff <= timedelta(days=30):
        print("checkActivity: ", member.display_name, "'s oldest message isn't 30 days old")
        # return "X - mH[0]<time(30days)"
        return -2

    # 3.
    if secondOldestMessageDiff >= timedelta(weeks=4):
        # await message.channel.send("Inactive: Not enogh recent activity")
        print(member.display_name, " doesn't have enough recent activity")
        # return "X - mH[1]>time(4weeks)"
        return -3
    print("checkActivity: ", member.display_name, " passed")
    # return "Y - passed"
    return True


def checkActivity(message, memberId):
    if not _m.helper.message_in_asbestos(message):
        print("ERROR: checkActivity: run outside of asbestos")
        return
    print("Running checkActivity")
    member = message.guild.get_member(memberId)
    if member is None or member.joined_at is None:
        print(str(memberId)+" is not in the guild")
        # return "X - !in guild"
        return -4

    # anyone with the bot role will always be marked active
    if any(role.id == 1290163512865456171 for role in member.roles):
        print("checkActivity: User is a bot")
        # return "Y - bot"
        return True
    # 3 requirements:
    #1. 10 msgs in msg history:
    #2. msg[0] (the oldest ever) must be 30 days old:
    #3. msg[1] (second oldest) must be less than 4 weeks old
    # print(len(_m.perma_data["last_message_dates"][memberId]))

    # 1.
    if len(_m.perma_data["last_message_dates"][memberId]) != 10:
        print("checkActivity: ", member.display_name, "has too few messages")
        # return "X - <10 mesg"
        return -1
        
    oldestMessageDiff = (datetime.now(timezone.utc) - datetime.fromisoformat(_m.perma_data["last_message_dates"][memberId][0]))
    secondOldestMessageDiff = (datetime.now(timezone.utc) - datetime.fromisoformat(_m.perma_data["last_message_dates"][memberId][1]))
    # await message.channel.send("1st diff: " + str(oldestMessageDiff) + "\n2nd diff: " + str(secondOldestMessageDiff) + "\nsize: " + str(len(_m.perma_data["last_message_dates"][memberId])))
    # print(str(oldestMessageDiff) +"\n"+ str(secondOldestMessageDiff))

    # 2.
    if oldestMessageDiff <= timedelta(days=30) and (datetime.now(timezone.utc) - member.joined_at) < timedelta(days=60):
        print("checkActivity: ", member.display_name, "'s oldest message isn't 30 days old")
        # return "X - mH[0]<time(30days)"
        return -2

    # 3.
    if secondOldestMessageDiff >= timedelta(weeks=4):
        # await message.channel.send("Inactive: Not enogh recent activity")
        print(member.display_name, " doesn't have enough recent activity")
        # return "X - mH[1]>time(4weeks)"
        return -3
    print("checkActivity: ", member.display_name, " passed")
    # return "Y - passed"
    return True



async def setActive(message, memberId): # active role id = 1416664166365790359
    # if not activeRole:
    #     activeRole = message.guild.get_role(activeId)
    # if not inactiveRole:
    #     inactiveRole = message.guild.get_role(inactiveId)
    global activeRole
    global inactiveRole
    if activeRole is None:
        activeRole = message.guild.get_role(activeId)
    if inactiveRole is None:
        inactiveRole = message.guild.get_role(inactiveId)
    
    # await message.channel.send(str(message.guild.members)[:2000])
    output = ""
    for member in message.guild.members:
        if member.id == memberId:
            # output+= str(member) + " is "
            output += str(member.display_name)
            if any(role.id == activeId for role in member.roles):
                # await message.channel.send(str(member)+" has active role")
                # output+="active"
                pass
            else:
                # output+="active"
                try:
                    await member.add_roles(activeRole)
                except:
                    await message.channel.send("ERROR: Could not edit member "+member.name+"'s roles")
                    await message.author.send("ERROR: Could not edit member "+str(member.id)+"'s roles")

                # await message.channel.send("Gave "+str(member)+" active role")

            if any(role.id == inactiveId for role in member.roles):
                try:
                    await member.remove_roles(inactiveRole)
                except:
                    await message.channel.send("ERROR: Could not edit member "+member.name+"'s roles")
                    await message.author.send("ERROR: Could not edit member "+str(member.id)+"'s roles")

                # await message.channel.send(str(member)+" lost inactive role")
            else:
                # await message.channel.send(str(member)+" doesn't have inactive role")
                pass

            break
    if len(output) > 0:
        return output
    else:
        print("ERROR: "+str(memberId)+" is not a valid member id")
        return


async def setMemberActive(message, member): # active role id = 1416664166365790359
    # if not activeRole:
    #     activeRole = message.guild.get_role(activeId)
    # if not inactiveRole:
    #     inactiveRole = message.guild.get_role(inactiveId)
    global activeRole
    global inactiveRole
    if activeRole is None:
        activeRole = message.guild.get_role(activeId)
    if inactiveRole is None:
        inactiveRole = message.guild.get_role(inactiveId)
    
    # await message.channel.send(str(message.guild.members)[:2000])
    output = ""

    # output+= str(member) + " is "
    output += str(member.display_name)
    print("setMemberActive currently disabled") # remove to allow
    return                                      # role editing

    if any(role.id == activeId for role in member.roles):
        # await message.channel.send(str(member)+" has active role")
        # output+="active"
        pass
    else:
        # output+="active"
        try:
            await member.add_roles(activeRole)
        except:
            await message.channel.send("ERROR: Could not edit member "+member.name+"'s roles")
            await message.author.send("ERROR: Could not edit member "+str(member.id)+"'s roles")

        # await message.channel.send("Gave "+str(member)+" active role")

    if any(role.id == inactiveId for role in member.roles):
        try:
            await member.remove_roles(inactiveRole)
        except:
            await message.channel.send("ERROR: Could not edit member "+member.name+"'s roles")
            await message.author.send("ERROR: Could not edit member "+str(member.id)+"'s roles")

        # await message.channel.send(str(member)+" lost inactive role")
    else:
        # await message.channel.send(str(member)+" doesn't have inactive role")
        pass

    return output



async def setMemberInactive(message, member): # inactive role id = 1416664311815868518
    global activeRole
    global inactiveRole
    if activeRole is None:
        activeRole = message.guild.get_role(activeId)
    if inactiveRole is None:
        inactiveRole = message.guild.get_role(inactiveId)

    # await message.channel.send(str(message.guild.members)[:2000])
    output = str(member.display_name) #+ " is "
    print("setMemberInactive currently disabled") # remove to allow
    return                                        # role editing

    if any(role.id == activeId for role in member.roles):
        try:
            await member.remove_roles(activeRole)
        except:
            await message.channel.send("ERROR: Could not edit member "+member.name+"'s roles")
            await message.author.send("ERROR: Could not edit member "+str(member.id)+"'s roles")
            return

        # await message.channel.send(str(member)+" lost active role")
    else:
        # await message.channel.send(""+str(member)+" doesn't have active role")
        pass

    if any(role.id == inactiveId for role in member.roles):
        # await message.channel.send(str(member)+" already has inactive role")
        # output+= "inactive"
        pass
    else:
        # output+="inactive"
        try:
            await member.add_roles(inactiveRole)
        except:
            await message.channel.send("ERROR: Could not edit member "+member.name+"'s roles")
            await message.author.send("ERROR: Could not edit member "+str(member.id)+"'s roles")
            return

        # await message.channel.send(str(member)+" gained inactive role")
    return output



async def setInactive(message, memberId): # inactive role id = 1416664311815868518
    global activeRole
    global inactiveRole
    if activeRole is None:
        activeRole = message.guild.get_role(activeId)
    if inactiveRole is None:
        inactiveRole = message.guild.get_role(inactiveId)

    # await message.channel.send(str(message.guild.members)[:2000])
    output = ""
    for member in message.guild.members:
        if member.id == memberId:
            output += str(member.display_name) #+ " is "
            if any(role.id == activeId for role in member.roles):
                try:
                    await member.remove_roles(activeRole)
                except:
                    await message.channel.send("ERROR: Could not edit member "+member.name+"'s roles")
                    await message.author.send("ERROR: Could not edit member "+str(member.id)+"'s roles")
                    return

                # await message.channel.send(str(member)+" lost active role")
            else:
                # await message.channel.send(""+str(member)+" doesn't have active role")
                pass

            if any(role.id == inactiveId for role in member.roles):
                # await message.channel.send(str(member)+" already has inactive role")
                # output+= "inactive"
                pass
            else:
                # output+="inactive"
                try:
                    await member.add_roles(inactiveRole)
                except:
                    await message.channel.send("ERROR: Could not edit member "+member.name+"'s roles")
                    await message.author.send("ERROR: Could not edit member "+str(member.id)+"'s roles")
                    return

                # await message.channel.send(str(member)+" gained inactive role")
            break
    if len(output) > 0:
        return output
    else:
        print("ERRPR: "+str(memberId)+" is not a valid member id")
        return

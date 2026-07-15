import __main__ as _m
import settings as _s


#----------------functions--------------------

def save_sticky_data(name):
    with open('pickle_files/'+str(name)+'.pkl', 'wb') as f:
        _m.pickle.dump(_m.perma_data[name], f)


def is_five_minutes_past(datetime1):
    """Checks if datetime1 is at least 5 minutes ago."""
    time_difference = _m.datetime.datetime.utcnow() - datetime1
    return time_difference >= _m.datetime.timedelta(minutes=5)


def count_user_quotes(user_id):
    u = str(user_id)
    count = 0
    for q, g, a in  _m.perma_data["all_quotes"]:
        if u in q:
            count+=1
    return count


def to_emoji_num(num):
    num=str(int(num)+1)
    number_emojis = ":zero: :one: :two: :three: :four: :five: :six: :seven: :eight: :nine:".split(" ")
    output = ""
    for n in num:
        output+=number_emojis[int(n)]
    return output


def message_in_asbestos(message):
    try: 
        if message.guild.id != 1277433994459353159:
            return False
    except:
        return False
    return True


async def sendLargeOutput(message, output, printAll=True):
    print(f"sendLargeOutput length = {len(output)}")

    # if output is below discord char limit, just print normally
    if len(output) < 2001:
        if len(output) < 1:
            return
        await message.channel.send(output)

    # recursively print entire output in chunks
    # attempt to find the last line to preserve line breaks
    elif printAll: 
        lastLine = output[:2000].rfind('\n')
        if lastLine <= 0: # -1 if .rfind finds nothing, or if the \n is at index 0 (can't send empty message)
            lastLine = 2000
        await message.channel.send(output[:lastLine])
        await sendLargeOutput(message, output[lastLine:], printAll)

    # print the first 2000 chars, minus a quirky message
    elif not printAll:
        errorMessage = "\n(and more)..."
        outputSize = output - len(errorMessage)
        await message.channel.send(output[:outputSize], errorMessage)
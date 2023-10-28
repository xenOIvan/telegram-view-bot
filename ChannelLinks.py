import configparser
import json
import asyncio
from numpy import random
import views as vw
import SendReaction as SR
from datetime import date, datetime
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.messages import (GetHistoryRequest)
from telethon.tl.types import (
    PeerChannel
)


# some functions to parse json date
class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        if isinstance(o, bytes):
            return list(o)

        return json.JSONEncoder.default(self, o)


# Reading Configs
config = configparser.ConfigParser()
config.read("config.ini")

# Setting configuration values
api_id = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']
reactionNumber = int(config['Telegram']['reactionNumber'])
OldViewsPercentage = float(config['Telegram']['OldViewsPercentage'])
#NoOfMessagesSkipped = int(config['Telegram']['NoOfPastMessagesSkipped'])

def linkToID(lnk):
    res1 = lnk.replace('https://t.me/', '').split('/')
    res2 = res1[1].split('?')
    return int(res2[0])


PastMessagesStartingID = linkToID(config['Telegram']['PastMessagesStartingID'])
PastMessagesEndingID = linkToID(config['Telegram']['PastMessagesEndingID'])

if PastMessagesEndingID < PastMessagesStartingID:
    temp = PastMessagesStartingID
    PastMessagesStartingID = PastMessagesEndingID
    PastMessagesEndingID = temp

api_hash = str(api_hash)

phone = config['Telegram']['phone']
username = config['Telegram']['username']

# Create the client and connect
client = TelegramClient(username, int(api_id), api_hash)
target_views = int(config['Telegram']['View_Limit'])
startingTarget_views = target_views
async def ViewAllPosts(phone):
    await client.start()
    print("Client Created")
    # Ensure you're authorized
    if await client.is_user_authorized() == False:
        await client.send_code_request(phone)
        try:
            await client.sign_in(phone, input('Enter the code: '))
        except SessionPasswordNeededError:
            await client.sign_in(password=input('Password: '))

    me = await client.get_me()

    user_input_channel = config['Telegram']['ChannelLink']

    if user_input_channel.isdigit():
        entity = PeerChannel(int(user_input_channel))
    else:
        entity = user_input_channel

    my_channel = await client.get_entity(entity)

    offset_id = 0
    limit = 100
    all_messages = []
    total_messages = 0
    total_count_limit = int(config['Telegram']['NoOfPastMessages']) + 1
    minreaction = int(config['Telegram']['minReactionType'])
    maxreaction = int(config['Telegram']['maxReactionType'])
    groupedPostsList = []

    def getReactionPallete():
        reactions = ['👍', '👌', '❤️', '😍', '🔥', '👏', '😁', '🤯', '😱', '🎉', '🤩', '🙏', '🕊', '💯', '⚡️', '🏆', '😇',
                     '🤗']
        ReactionPalette = []
        random.shuffle(reactions)

        typesOfReaction = random.randint(minreaction, maxreaction)

        if len(ReactionPalette) < typesOfReaction:
            for i in reactions:
                if len(ReactionPalette) < typesOfReaction:
                    if i not in ReactionPalette:
                        ReactionPalette.append(i)
                else:
                    break
        return ReactionPalette

    async def executeOnAllMessages(messagelimit):
        if len(all_messages) < messagelimit:
            messagelimit = len(all_messages)
        global target_views
        totalReactionsAlready = 0
        endReactionCount = False

        for x in range(0, messagelimit - 1):
            if PastMessagesEndingID >= all_messages[x].id >= PastMessagesStartingID:
                if x+1 <= messagelimit-1 and PastMessagesEndingID >= all_messages[x+1].id >= PastMessagesStartingID:
                    if all_messages[x+1].grouped_id != all_messages[x].grouped_id:
                        endReactionCount = True
                    elif all_messages[x+1].grouped_id is None and all_messages[x].grouped_id is None:
                        endReactionCount = True

                if (all_messages[x].reactions is not None) and hasattr(all_messages[x].reactions, 'results'):
                    for y in all_messages[x].reactions.results:
                        totalReactionsAlready = totalReactionsAlready + y.count

                if totalReactionsAlready <= 0 and endReactionCount:
                    print("Starting Reactions: \n")
                    await SR.run_SendReaction(all_messages[x].id, reactionNumber - totalReactionsAlready, getReactionPallete())

                if endReactionCount:
                    endReactionCount = False
                    totalReactionsAlready = 0


                if hasattr(all_messages[x], 'message') and all_messages[x].grouped_id not in groupedPostsList:
                    if all_messages[x].grouped_id is not None:
                        groupedPostsList.append(all_messages[x].grouped_id)

                    if all_messages[x].views < target_views:
                        print("Starting on Post No." + str(all_messages[x].id))
                        vw.beginSearch(config['Telegram']['ChannelLink'], all_messages[x].id, all_messages[x].views, False, target_views)

                    target_views = target_views + round(startingTarget_views * (OldViewsPercentage/100))
                    print(target_views)




        print("All Views are completed")


    while True:
        print("Current Offset ID is:", offset_id, "; Total Messages:", total_messages)
        history = await client(GetHistoryRequest(
            peer=my_channel,
            offset_id=offset_id,
            offset_date=None,
            add_offset=0,
            limit=limit,
            max_id=0,
            min_id=0,
            hash=0
        ))
        if not history.messages:
            await executeOnAllMessages(total_count_limit)
            break
        messages = history.messages
        for message in messages:
            all_messages.append(message)
        offset_id = messages[len(messages) - 1].id
        total_messages = len(all_messages)

        if total_count_limit != 0 and total_messages >= total_count_limit:
            await executeOnAllMessages(total_count_limit)
            break


with client:
    client.loop.run_until_complete(ViewAllPosts(phone))

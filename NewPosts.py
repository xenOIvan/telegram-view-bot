import configparser
import asyncio
from numpy import random
from telethon.sync import TelegramClient
import views as vw
import SendReaction as SR

threads=[]

# Setting configuration values
config = configparser.ConfigParser()
config.read("config.ini")
api_id = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']
phone = config['Telegram']['phone']
target_views = int(config['Telegram']['View_Limit'])

user_input_channel = config['Telegram']['ChannelLink']
user_input_channel = user_input_channel.replace('https://t.me/', '')
minreaction = int(config['Telegram']['minReactionType'])
maxreaction = int(config['Telegram']['maxReactionType'])
reactionNumber = int(config['Telegram']['reactionNumber'])
groupedPostsList = []


async def getClient(phone):
    try:
        print(f'Authenticating phone number: {phone}')
        client = TelegramClient(f'sessions/{phone}', api_id, api_hash)
        await client.start()

        if not await client.is_user_authorized():
            await client.send_code_request(phone)
            await client.sign_in(phone, input(f'Phone # ({phone}) Enter the code: '))
        return client
    except Exception as e:
        print(f'Error: {str(e)}')
        return None


async def getMessagesID(client,lastMessage):
    result = None
    try:
        previousMessageSearched = None
        async for message in client.iter_messages(user_input_channel):
            if lastMessage is None:
                return message, False
            elif message.id == lastMessage:
                if previousMessageSearched is None:
                    return message, False
                else:
                    return previousMessageSearched, False
            elif message.id < lastMessage:
                return 0, True
            previousMessageSearched = message
            print("Searching Next")
            #print(f'Message from {message.sender_id}: {message.text} : https://t.me/NIFTY_BANKNIFTY_CALLS_AND{message.id}')
    except Exception as e:
        print(f'Error while getting messages: {str(e)}')
        return result, True


async def executeMessages(msg):
    global groupedPostsList
    if hasattr(msg, 'message') and msg.grouped_id not in groupedPostsList:
        print("Running on message: " + msg.message)
        if msg.grouped_id is not None:
            groupedPostsList.append(msg.grouped_id)

        if msg.views < target_views:
            print("Starting on Post No." + str(msg.id))
            vw.beginSearch(config['Telegram']['ChannelLink'], msg.id, msg.views, True, 0)

        reactions = ['👍', '👌', '❤️', '😍', '🔥', '👏', '😁', '🤯', '😱', '🎉', '🤩', '🙏', '🕊', '💯', '⚡️', '🏆', '😇',
                     '🤗']
        ReactionPalette = []
        random.shuffle(reactions)

        totalReactionsAlready = 0
        if (msg.reactions is not None) and hasattr(msg.reactions, 'results'):
            for y in msg.reactions.results:
                totalReactionsAlready = totalReactionsAlready + y.count
                ReactionPalette.append(y.reaction.emoticon)

        typesOfReaction = random.randint(minreaction, maxreaction)

        if len(ReactionPalette) < typesOfReaction:
            for i in reactions:
                if len(ReactionPalette) < typesOfReaction:
                    if i not in ReactionPalette:
                        ReactionPalette.append(i)
                else:
                    break
        print(ReactionPalette)

        if totalReactionsAlready <= 0:
            print("Starting Reactions: \n")
            await SR.run_SendReaction(msg.id, reactionNumber - totalReactionsAlready, ReactionPalette)

    print("All Views are completed")


async def startBot():
    client = await getClient(phone)
    lastMessage = None
    
    if client is not None:
        print('Bot started.')
        while True:
            print("Waiting for New messages: ")
            msg, Reset = await getMessagesID(client, lastMessage)
            if Reset:
                lastMessage = None
                msg, temp = await getMessagesID(client, lastMessage)

            if lastMessage is None or lastMessage != msg.id:
                if lastMessage is not None:
                    await executeMessages(msg)
                lastMessage = msg.id
            await asyncio.sleep(10)

asyncio.run(startBot())
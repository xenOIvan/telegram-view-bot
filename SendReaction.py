import configparser
from numpy import random
import pandas as pd
from telethon.sync import TelegramClient
from telethon import functions, types
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.messages import SendReactionRequest
from telethon import utils
from telethon.tl.functions.channels import JoinChannelRequest


config = configparser.ConfigParser()
config.read("config.ini")

TimesExecuted = 0
#ApiHash = config['Telegram']['api_hash']

async def send_reaction(client, chat_id, message_id, ReactionPalette):
    global TimesExecuted
    TimesExecuted = TimesExecuted + 1
    try:
        random_reaction = random.choice(ReactionPalette)
        result = await client(SendReactionRequest(
                        peer=chat_id,
                        msg_id=message_id,
                        big=True,
                        add_to_recent=True,
                        reaction=[types.ReactionEmoji(
                            emoticon=random_reaction
                        )]
                    ))

        print(str(TimesExecuted) + " Reactions posted \n Result: " + str(result))
    except Exception as e:
        print("Error sending reaction:", str(e))


async def main(phone, ApiID, ApiHash, ReactionPalette, message_id):
    try:
        async with TelegramClient(f'sessions/{phone}', ApiID, ApiHash) as client:
            if not await client.is_user_authorized():
                print(f'{phone} needs to be authenticated by OTP')
                return

            chat_id = config['Telegram']['ChannelLink']
            chat_id = chat_id.replace('https://t.me/', '')

            await send_reaction(client, chat_id, message_id, ReactionPalette)
    except:
        pass

async def run_SendReaction(message_id, ReactionNumber, ReactionPalette):
    df = pd.read_csv('phone.csv')
    apiDf = pd.read_csv('Api.csv')

    global TimesExecuted
    TimesExecuted = 0

    for index, row in df.iterrows():
        if TimesExecuted > ReactionNumber:
            break
        num_rows = len(df)
        random_index = random.randint(0, num_rows - 1)
        selected_row = df.iloc[random_index]
        corresponding_api_row = apiDf.iloc[random_index]
        api = corresponding_api_row['API']
        hash_value = corresponding_api_row['Hash']
        phone = selected_row['Phone'] #row['Phone']
        print(phone)
        await main(phone, api, hash_value, ReactionPalette, message_id)


#asyncio.run(run_SendReaction(18,25))

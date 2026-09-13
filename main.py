import os
from telethon import TelegramClient, events

api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')
source_chat = os.getenv('SOURCE_CHAT')
destination_chat = os.getenv('DESTINATION_CHAT')
old_link = os.getenv('OLD_LINK')
new_link = os.getenv('NEW_LINK')

client = TelegramClient('bot_session', api_id, api_hash).start(bot_token=bot_token)

@client.on(events.NewMessage(chats=source_chat))
async def handler(event):
    text = event.raw_text or ""
    if old_link and new_link:
        text = text.replace(old_link, new_link)
    
    if event.media:
        await client.send_file(destination_chat, event.media, caption=text)
    else:
        await client.send_message(destination_chat, text)

print("Bot started successfully...")
client.run_until_disconnected()

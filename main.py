import os
from telethon import TelegramClient, events

api_id = int(os.environ.get("API_ID"))
api_hash = os.environ.get("API_HASH")
source_chat = os.environ.get("SOURCE_CHAT")
destination_chat = os.environ.get("DESTINATION_CHAT")
old_link = os.environ.get("OLD_LINK", "")
new_link = os.environ.get("NEW_LINK", "")

client = TelegramClient('cloud_session', api_id, api_hash)

@client.on(events.NewMessage(chats=source_chat))
async def handler(event):
    text = event.raw_text or ""
    
    if old_link and new_link:
        text = text.replace(old_link, new_link)
    
    if event.media:
        await client.send_file(destination_chat, event.media, caption=text)
    else:
        await client.send_message(destination_chat, text)

client.start()
client.run_until_disconnected()

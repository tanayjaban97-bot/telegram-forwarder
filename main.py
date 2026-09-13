import os
import threading
from flask import Flask
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# Render Web Service port bind karne ke liye Flask App
app = Flask(__name__)

@app.route('/')
def home():
    return "Telegram Forwarder is Active!"

def run_flask():
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

threading.Thread(target=run_flask, daemon=True).start()

# Telegram User Session Config
api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')
session_string = os.getenv('STRING_SESSION')
source_chat = os.getenv('SOURCE_CHAT')
destination_chat = os.getenv('DESTINATION_CHAT')
old_link = os.getenv('OLD_LINK')
new_link = os.getenv('NEW_LINK')

client = TelegramClient(StringSession(session_string), api_id, api_hash).start()

@client.on(events.NewMessage(chats=source_chat))
async def handler(event):
    text = event.raw_text or ""
    if old_link and new_link:
        text = text.replace(old_link, new_link)
    
    if event.media:
        await client.send_file(destination_chat, event.media, caption=text)
    else:
        await client.send_message(destination_chat, text)

print("User account bot started successfully...")
client.run_until_disconnected()

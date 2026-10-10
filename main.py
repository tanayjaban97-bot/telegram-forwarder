import os
import re
import asyncio
from flask import Flask
from threading import Thread
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError

# Render Port Setup & Flask Keep-Alive
app = Flask(__name__)

@app.route('/')
def home():
    return "Telegram Forwarder Bot is Running 24/7!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# Read Environment Variables
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
STRING_SESSION = os.environ.get("STRING_SESSION")

def parse_env_list(env_var_name):
    val = os.environ.get(env_var_name, "")
    return [item.strip() for item in val.split(",") if item.strip()]

SOURCE_CHATS = parse_env_list("SOURCE_CHAT")
DEST_CHATS = parse_env_list("DESTINATION_CHAT")
OLD_LINKS = parse_env_list("OLD_LINK")
NEW_LINKS = parse_env_list("NEW_LINK")

# Map Source to Destination & Links
MAPPING = {}
for i in range(len(SOURCE_CHATS)):
    src = SOURCE_CHATS[i].lower()
    dest = DEST_CHATS[i] if i < len(DEST_CHATS) else None
    old_l = OLD_LINKS[i] if i < len(OLD_LINKS) else ""
    new_l = NEW_LINKS[i] if i < len(NEW_LINKS) else ""
    
    if dest:
        MAPPING[src] = {
            "dest": dest,
            "old_link": old_l,
            "new_link": new_l
        }

from telethon.sessions import StringSession
client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)

@client.on(events.NewMessage)
async def message_handler(event):
    try:
        chat = await event.get_chat()
        chat_username = getattr(chat, 'username', None)
        
        # Check matching channel
        matched_src = None
        if chat_username:
            formatted_username = f"@{chat_username.lower()}"
            for src in MAPPING.keys():
                if src.lower() == formatted_username:
                    matched_src = src
                    break
        
        if not matched_src:
            return

        config = MAPPING[matched_src]
        target_dest = config["dest"]
        old_link = config["old_link"]
        new_link = config["new_link"]

        text = event.message.message or ""
        
        # Link Replacement
        if old_link and new_link and old_link in text:
            text = text.replace(old_link, new_link)

        # Forwarding Logic
        if event.message.media:
            await client.send_message(target_dest, text, file=event.message.media)
        elif text:
            await client.send_message(target_dest, text)
            
        print(f"[SUCCESS] Message forwarded from {matched_src} to {target_dest}")

    except FloodWaitError as e:
        print(f"[FLOOD WAIT] Sleeping for {e.seconds} seconds...")
        await asyncio.sleep(e.seconds)
    except Exception as e:
        print(f"[ERROR] {e}")

async def main():
    print("Starting Telegram Client...")
    await client.start()
    print("Bot status: FULLY ACTIVE 24/7 & Listening for messages...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    # Start Flask Web Server Thread
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Run Telethon Loop
    asyncio.run(main())

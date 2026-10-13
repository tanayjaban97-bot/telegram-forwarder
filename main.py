import os
import re
import asyncio
from flask import Flask
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# --- Flask Server for Render Keep-Alive ---
app = Flask('')

@app.route('/')
def home():
    return "Bot status: FULLY ACTIVE 24/7 & Listening for messages..."

def run_flask():
    app.run(host='0.0.0.0', port=10000)

# --- Telegram Credentials & Configuration ---
API_ID = int(os.environ.get("API_ID", 30611492))
API_HASH = os.environ.get("API_HASH", "b3171b81902e76cbbcd7f1d7e8470b88")
STRING_SESSION = os.environ.get("STRING_SESSION", "")

# Destination channel where messages will be forwarded
DESTINATION_CHANNEL = "headagentrr"

# Source channels list
SOURCE_CHANNELS = [
    "bigsmallmaster11",
    "MaanVip_bitcoin"
]

# Your Affiliate Link for replacement
AFFILIATE_LINK = "https://maanwin.ai/register?inviteCode=9HJ2BXN&from=web"

client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)

def replace_links_in_text(text):
    if not text:
        return text
    # Regex to find standard http/https links, www links, or t.me links
    url_pattern = re.compile(r'https?://[^\s]+|t\.me/[^\s]+|www\.[^\s]+', re.IGNORECASE)
    return url_pattern.sub(AFFILIATE_LINK, text)

# Cache to prevent duplicate processing of media albums
processed_albums = set()

@client.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def handler(event):
    try:
        # 1. Skip if message contains any APK file
        if event.file and event.file.name:
            if event.file.name.lower().endswith('.apk'):
                print("[SKIPPED] APK file detected and blocked.")
                return

        # 2. Handle Media Groups / Albums (Multiple photos together)
        if event.grouped_id:
            if event.grouped_id in processed_albums:
                return
            
            processed_albums.add(event.grouped_id)
            asyncio.get_event_loop().call_later(45, processed_albums.discard, event.grouped_id)

            # Short wait to let all parts of the album arrive
            await asyncio.sleep(1.5)
            
            messages = await client.get_messages(event.chat_id, limit=10)
            group_msgs = [msg for msg in messages if msg.grouped_id == event.grouped_id]

            media_files = []
            album_caption = ""

            for msg in group_msgs:
                if msg.file and msg.file.name and msg.file.name.lower().endswith('.apk'):
                    continue
                if msg.media:
                    media_files.append(msg.media)
                if msg.raw_text and not album_caption:
                    album_caption = replace_links_in_text(msg.raw_text)

            if media_files:
                media_files.reverse() # Maintain original order
                await client.send_file(DESTINATION_CHANNEL, media_files, caption=album_caption)
                print(f"[SUCCESS] Album forwarded to {DESTINATION_CHANNEL}")
            return

        # 3. Single Message Handling (Text or Media)
        message_text = event.raw_text
        modified_text = replace_links_in_text(message_text)

        if event.media:
            await client.send_file(DESTINATION_CHANNEL, event.media, caption=modified_text)
        elif modified_text:
            await client.send_message(DESTINATION_CHANNEL, modified_text)

        print(f"[SUCCESS] Message forwarded to {DESTINATION_CHANNEL}")

    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    import threading
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    print("Starting Telegram Client...")
    client.start()
    print("Bot is running and listening for messages...")
    client.run_until_disconnected()

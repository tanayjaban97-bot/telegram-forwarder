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

# --- Telegram Credentials ---
API_ID = int(os.environ.get("API_ID", 30611492))
API_HASH = os.environ.get("API_HASH", "b3171b81902e76cbbcd7f1d7e8470b88")
STRING_SESSION = os.environ.get("STRING_SESSION", "")

# --- Mapping Configuration ---
# Source Channel Username (lowercase) -> (Destination Channel, Unique Affiliate Link)
CHANNEL_MAPPING = {
    "bigsmallmaster11": {
        "destination": "SixClubWinningZone",
        "affiliate_link": "https://www.o0zd1g.com/#/register?invitationCode=645536043193"
    },
    "crypto_dmfirstofficiall": {
        "destination": "predictionmasterhindi",
        "affiliate_link": "https://www.dmfirst13.com/#/register?invitationCode=52199550527"
    },
    "maanvip_bitcoin": {
        "destination": "headagentrr",
        "affiliate_link": "https://maanwin.ai/register?inviteCode=9HJ2BXN&from=web"
    }
}

SOURCE_CHANNELS = list(CHANNEL_MAPPING.keys())

client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)

def replace_links_in_text(text, replacement_link):
    if not text:
        return text
    # Regex to find standard URLs, t.me links, or www links
    url_pattern = re.compile(r'https?://[^\s]+|t\.me/[^\s]+|www\.[^\s]+', re.IGNORECASE)
    return url_pattern.sub(replacement_link, text)

processed_albums = set()

@client.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def handler(event):
    try:
        # Determine source chat username
        chat = await event.get_chat()
        chat_username = getattr(chat, 'username', '').lower() if getattr(chat, 'username', None) else ""

        if not chat_username or chat_username not in CHANNEL_MAPPING:
            # Fallback check if username matches any key
            for key in CHANNEL_MAPPING:
                if key in str(event.chat_id) or (getattr(chat, 'username', '') and key == chat.username.lower()):
                    chat_username = key
                    break

        if chat_username not in CHANNEL_MAPPING:
            return

        config = CHANNEL_MAPPING[chat_username]
        dest_channel = config["destination"]
        affiliate_link = config["affiliate_link"]

        # 1. Skip if message contains any APK file
        if event.file and event.file.name:
            if event.file.name.lower().endswith('.apk'):
                print(f"[SKIPPED] APK file detected from {chat_username}.")
                return

        # 2. Handle Media Groups / Albums
        if event.grouped_id:
            if event.grouped_id in processed_albums:
                return
            
            processed_albums.add(event.grouped_id)
            asyncio.get_event_loop().call_later(45, processed_albums.discard, event.grouped_id)

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
                    album_caption = replace_links_in_text(msg.raw_text, affiliate_link)

            if media_files:
                media_files.reverse()
                await client.send_file(dest_channel, media_files, caption=album_caption)
                print(f"[SUCCESS] Album forwarded from {chat_username} -> {dest_channel}")
            return

        # 3. Single Message Handling
        message_text = event.raw_text
        modified_text = replace_links_in_text(message_text, affiliate_link)

        if event.media:
            await client.send_file(dest_channel, event.media, caption=modified_text)
        elif modified_text:
            await client.send_message(dest_channel, modified_text)

        print(f"[SUCCESS] Message forwarded from {chat_username} -> {dest_channel}")

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

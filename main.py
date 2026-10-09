import os
import re
import asyncio
import urllib.request
from flask import Flask
from threading import Thread
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError

# --- FLASK KEEP-ALIVE SERVER ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot status: FULLY ACTIVE 24/7"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

Thread(target=run_flask, daemon=True).start()

# --- HARDENED SELF-PING SYSTEM ---
def self_ping():
    import time
    render_url = os.environ.get("RENDER_EXTERNAL_URL", "")
    while True:
        time.sleep(120)
        if render_url:
            try:
                urllib.request.urlopen(render_url, timeout=10)
            except Exception:
                pass

Thread(target=self_ping, daemon=True).start()

# --- CONFIGURATION FROM RENDER ENV ---
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
STRING_SESSION = os.environ.get("STRING_SESSION", "")

SOURCE_INPUT = os.environ.get("SOURCE_CHAT", "@Bigsmallmaster11")
DEST_INPUT = os.environ.get("DESTINATION_CHAT", "@SixClubWinningZone")

OLD_LINK_INPUT = os.environ.get("OLD_LINK", "").strip()
NEW_LINK_INPUT = os.environ.get("NEW_LINK", "").strip()

sources = [s.strip() for s in SOURCE_INPUT.split(",") if s.strip()]
destinations = [d.strip() for d in DEST_INPUT.split(",") if d.strip()]
old_links = [o.strip() for o in OLD_LINK_INPUT.split(",") if o.strip()]
new_links = [n.strip() for n in NEW_LINK_INPUT.split(",") if n.strip()]

CHANNEL_MAP = {}
for i in range(len(sources)):
    dest = destinations[i] if i < len(destinations) else destinations[0]
    old_l = old_links[i] if i < len(old_links) else (old_links[0] if old_links else "")
    new_l = new_links[i] if i < len(new_links) else (new_links[0] if new_links else "")
    
    CHANNEL_MAP[sources[i]] = {
        "dest": dest,
        "old_link": old_l,
        "new_link": new_l
    }

client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)

def process_text(text, channel_config):
    if not text:
        return ""
    
    dest_chat = channel_config["dest"]
    old_l = channel_config["old_link"]
    new_l = channel_config["new_link"]
    dest_handle = dest_chat.replace("@", "")

    if old_l and new_l:
        text = text.replace(old_l, new_l)
    elif new_l:
        text = re.sub(r'https?://[^\s]+', new_l, text)

    text = re.sub(r't\.me/[a-zA-Z0-9_]+', f't.me/{dest_handle}', text)
    text = re.sub(r'@[a-zA-Z0-9_]+', dest_chat, text)
    
    return text

async def get_my_saved_apk():
    try:
        async for msg in client.iter_messages('me', limit=20):
            if msg.file and msg.file.name and msg.file.name.endswith('.apk'):
                return msg.media
    except Exception as e:
        print(f"[ERROR] APK read error: {e}")
    return None

album_cache = {}

@client.on(events.NewMessage(chats=list(CHANNEL_MAP.keys())))
async def handler(event):
    try:
        chat_entity = await event.get_chat()
        source_handle = f"@{chat_entity.username}" if chat_entity.username else str(event.chat_id)
        
        config = CHANNEL_MAP.get(source_handle) or CHANNEL_MAP.get(str(event.chat_id)) or list(CHANNEL_MAP.values())[0]
        target_dest = config["dest"]

        print(f"[NEW MESSAGE] From: {source_handle} -> To: {target_dest}")

        is_apk = False
        if event.file and event.file.name and event.file.name.endswith('.apk'):
            is_apk = True

        updated_text = process_text(event.raw_text, config)

        if is_apk:
            my_apk_media = await get_my_saved_apk()
            if my_apk_media:
                await client.send_file(target_dest, my_apk_media, caption=updated_text)
            else:
                await client.send_message(target_dest, updated_text)
            return

        if event.grouped_id:
            if event.grouped_id not in album_cache:
                album_cache[event.grouped_id] = True
                await asyncio.sleep(2.5)
                
                messages = await client.get_messages(event.chat_id, limit=10)
                group = [m for m in messages if m.grouped_id == event.grouped_id]
                
                media_list = []
                caption_text = ""
                for msg in reversed(group):
                    if msg.media:
                        media_list.append(msg.media)
                    if msg.raw_text and not caption_text:
                        caption_text = process_text(msg.raw_text, config)

                if media_list:
                    await client.send_file(target_dest, media_list, caption=caption_text)
            return

        if event.media:
            await client.send_file(target_dest, event.media, caption=updated_text)
        else:
            if updated_text:
                await client.send_message(target_dest, updated_text)

    except FloodWaitError as fwe:
        await asyncio.sleep(fwe.seconds + 2)
    except Exception as err:
        print(f"[ERROR] Handler issue: {err}")

async def main():
    while True:
        try:
            await client.start()
            await client.run_until_disconnected()
        except Exception as crash_err:
            await asyncio.sleep(3)

if __name__ == "__main__":
    asyncio.run(main())

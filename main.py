import os
import re
import asyncio
from flask import Flask
from threading import Thread
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# --- FLASK KEEP ALIVE ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Master Bot is running 24/7!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

Thread(target=run_flask, daemon=True).start()

# --- TELEGRAM CONFIGURATION ---
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
STRING_SESSION = os.environ.get("STRING_SESSION", "")

SOURCE_CHAT = "@sixclubofficialchanel"
DESTINATION_CHAT = "@SixClubWinningZone"

# Settings
MY_NEW_LINK = "https://www.o0zd1g.com/#/register?invitationCode=645536043193"
CUSTOM_FOOTER = "\n\n📌 **Join Official Channel:** @SixClubWinningZone"

client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)

def process_text(text):
    if not text:
        return ""

    # 1. Replace all external website links
    text = re.sub(r'https?://[^\s]+', MY_NEW_LINK, text)
    
    # 2. Replace Telegram channel links
    text = re.sub(r't\.me/[^\s]+', DESTINATION_CHAT, text)

    # 3. Add Custom Footer
    text += CUSTOM_FOOTER

    return text

@client.on(events.NewMessage(chats=SOURCE_CHAT))
async def handler(event):
    try:
        updated_text = process_text(event.raw_text)

        # Handle Albums / Grouped Photos
        if event.grouped_id:
            try:
                await client.send_file(
                    DESTINATION_CHAT, 
                    event.message.media, 
                    caption=updated_text
                )
            except Exception as e:
                print(f"Grouped media error: {e}")
            return

        # Handle Single Media (Photos, Videos, GIFs)
        if event.media:
            try:
                await client.send_file(DESTINATION_CHAT, event.media, caption=updated_text)
            except Exception as media_err:
                print(f"Media fail fallback to text: {media_err}")
                if updated_text:
                    await client.send_message(DESTINATION_CHAT, updated_text)
        else:
            if updated_text:
                await client.send_message(DESTINATION_CHAT, updated_text)

    except Exception as e:
        print(f"Master Handler Error: {e}")

async def main():
    print("Starting Master Telegram Forwarder Client...")
    await client.start()
    print("Master Client running successfully!")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())

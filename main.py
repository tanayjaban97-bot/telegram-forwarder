import os
import re
import asyncio
from flask import Flask
from threading import Thread
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# --- FLASK DUMMY SERVER (Keep Render Alive) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running 24/7!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# Start Flask server in background thread
Thread(target=run_flask, daemon=True).start()

# --- TELEGRAM CONFIGURATION ---
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
STRING_SESSION = os.environ.get("STRING_SESSION", "")

# Channels setup
SOURCE_CHAT = "@sixclubofficialchanel"
DESTINATION_CHAT = "@SixClubWinningZone"

client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)

@client.on(events.NewMessage(chats=SOURCE_CHAT))
async def handler(event):
    try:
        text = event.raw_text or ""

        # --- AUTO LINK REPLACEMENT LOGIC ---
        # Replace any t.me links with your channel handle or custom link
        if text:
            text = re.sub(r'https?://t\.me/\S+', DESTINATION_CHAT, text)

        # --- MEDIA HANDLING WITH PREMIUM FALLBACK ---
        if event.media:
            try:
                # Try sending file with updated text
                await client.send_file(DESTINATION_CHAT, event.media, caption=text)
            except Exception as media_err:
                print(f"Media Error (e.g., Premium Sticker/File): {media_err}")
                # Fallback: Send text only if media fails due to Telegram Premium limits
                if text:
                    await client.send_message(DESTINATION_CHAT, text)
        else:
            if text:
                await client.send_message(DESTINATION_CHAT, text)

    except Exception as e:
        print(f"General Handling Error: {e}")

async def main():
    print("Starting Telegram Forwarder Client...")
    await client.start()
    print("User account bot started successfully!")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())

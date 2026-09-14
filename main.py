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

Thread(target=run_flask, daemon=True).start()

# --- TELEGRAM CONFIGURATION ---
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
STRING_SESSION = os.environ.get("STRING_SESSION", "")

SOURCE_CHAT = "@sixclubofficialchanel"
DESTINATION_CHAT = "@SixClubWinningZone"

# Aapka Naya Referral Link
MY_NEW_LINK = "https://www.o0zd1g.com/#/register?invitationCode=645536043193"

client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)

@client.on(events.NewMessage(chats=SOURCE_CHAT))
async def handler(event):
    try:
        text = event.raw_text or ""

        # --- ADVANCED LINK REPLACEMENT LOGIC ---
        if text:
            # Matches any zgollb.com, o0zd1g.com, t.me, or generic http/https URLs
            text = re.sub(r'https?://[^\s]+', MY_NEW_LINK, text)
            text = re.sub(r't\.me/[^\s]+', DESTINATION_CHAT, text)

        # --- MEDIA HANDLING WITH PREMIUM FALLBACK ---
        if event.media:
            try:
                await client.send_file(DESTINATION_CHAT, event.media, caption=text)
            except Exception as media_err:
                print(f"Media Error (e.g., Premium Sticker/File): {media_err}")
                if text:
                    await client.send_message(DESTINATION_CHAT, text)
        else:
            if text:
                await client.send_message(DESTINATION_CHAT, text)

    except Exception as e:
        print(f"General Error: {e}")

async def main():
    print("Starting Telegram Forwarder Client...")
    await client.start()
    print("User account bot started successfully!")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())

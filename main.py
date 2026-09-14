import os
import re
import asyncio
import urllib.request
from flask import Flask
from threading import Thread
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# --- FLASK KEEP-ALIVE SERVER ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Forwarder Bot is Active 24/7!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

Thread(target=run_flask, daemon=True).start()

# --- SELF-PING SYSTEM (Prevents Render Sleep) ---
def self_ping():
    import time
    render_url = os.environ.get("RENDER_EXTERNAL_URL", "")
    while True:
        time.sleep(300)  # Ping every 5 minutes
        if render_url:
            try:
                urllib.request.urlopen(render_url)
                print("Keep-Alive Ping Sent!")
            except Exception as e:
                print(f"Ping Error: {e}")

Thread(target=self_ping, daemon=True).start()

# --- TELEGRAM CONFIGURATION ---
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
STRING_SESSION = os.environ.get("STRING_SESSION", "")

SOURCE_CHAT = "@sixclubofficialchanel"
DESTINATION_CHAT = "@SixClubWinningZone"

MY_NEW_LINK = "https://www.o0zd1g.com/#/register?invitationCode=645536043193"
CUSTOM_FOOTER = "\n\n📌 **Join Official Channel:** @SixClubWinningZone"

client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)

def process_text(text):
    if not text:
        return ""
    # External Site Links Replacement
    text = re.sub(r'https?://[^\s]+', MY_NEW_LINK, text)
    # Telegram Links Replacement
    text = re.sub(r't\.me/[^\s]+', DESTINATION_CHAT, text)
    # Footer Append
    text += CUSTOM_FOOTER
    return text

@client.on(events.NewMessage(chats=SOURCE_CHAT))
async def handler(event):
    try:
        updated_text = process_text(event.raw_text)

        # Handle Albums / Multiple Photos
        if event.grouped_id:
            try:
                await client.send_file(
                    DESTINATION_CHAT, 
                    event.message.media, 
                    caption=updated_text
                )
            except Exception as e:
                print(f"Album send error: {e}")
            return

        # Handle Single Media (Photos, Videos, GIFs)
        if event.media:
            try:
                await client.send_file(DESTINATION_CHAT, event.media, caption=updated_text)
            except Exception as media_err:
                print(f"Media error (Premium Fallback): {media_err}")
                if updated_text:
                    await client.send_message(DESTINATION_CHAT, updated_text)
        else:
            if updated_text:
                await client.send_message(DESTINATION_CHAT, updated_text)

    except Exception as e:
        print(f"Handler error: {e}")

async def main():
    while True:
        try:
            print("Connecting client to Telegram...")
            await client.start()
            print("Bot fully operational and listening!")
            await client.run_until_disconnected()
        except Exception as err:
            print(f"Disconnect detected: {err}. Auto-reconnecting in 5 seconds...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())

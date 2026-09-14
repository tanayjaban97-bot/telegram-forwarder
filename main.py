import os
import re
import asyncio
import urllib.request
from flask import Flask
from threading import Thread
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError, RPCError

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
        time.sleep(120)  # Ping every 2 minutes
        if render_url:
            try:
                urllib.request.urlopen(render_url, timeout=10)
                print("[SYSTEM] Keep-alive ping successfully delivered.")
            except Exception as e:
                print(f"[SYSTEM] Ping attempt skipped: {e}")

Thread(target=self_ping, daemon=True).start()

# --- CONFIGURATION ---
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
STRING_SESSION = os.environ.get("STRING_SESSION", "")

SOURCE_CHAT = "@sixclubofficialchanel"
DESTINATION_CHAT = "@SixClubWinningZone"

MY_NEW_LINK = "https://www.o0zd1g.com/#/register?invitationCode=645536043193"

client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)

def process_text(text):
    if not text:
        return ""
    # External Site Links Replacement
    text = re.sub(r'https?://[^\s]+', MY_NEW_LINK, text)
    # Telegram Links Replacement
    text = re.sub(r't\.me/[^\s]+', DESTINATION_CHAT, text)
    return text

@client.on(events.NewMessage(chats=SOURCE_CHAT))
async def handler(event):
    updated_text = process_text(event.raw_text)
    
    # Retry Mechanism for Telegram Limit Bypassing
    for attempt in range(3):
        try:
            if event.grouped_id:
                await client.send_file(DESTINATION_CHAT, event.message.media, caption=updated_text)
                break
            elif event.media:
                await client.send_file(DESTINATION_CHAT, event.media, caption=updated_text)
                break
            else:
                if updated_text:
                    await client.send_message(DESTINATION_CHAT, updated_text)
                break

        except FloodWaitError as fwe:
            print(f"[RATE LIMIT] Telegram forced wait for {fwe.seconds} seconds.")
            await asyncio.sleep(fwe.seconds + 2)
        except RPCError as rpc_err:
            print(f"[TELETHON RPC ERROR] {rpc_err}")
            if event.raw_text:
                await client.send_message(DESTINATION_CHAT, updated_text)
            break
        except Exception as err:
            print(f"[GENERAL ERROR] Attempt {attempt + 1} failed: {err}")
            await asyncio.sleep(2)

async def main():
    while True:
        try:
            print("[STATUS] Starting userbot listener...")
            await client.start()
            print("[STATUS] Bot is live and capturing all incoming posts.")
            await client.run_until_disconnected()
        except Exception as crash_err:
            print(f"[CRASH PREVENTED] Reconnecting immediately: {crash_err}")
            await asyncio.sleep(3)

if __name__ == "__main__":
    asyncio.run(main())

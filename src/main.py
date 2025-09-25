# src/main.py
import os, fcntl, sys
import time
import json
import sqlite3
from pathlib import Path

# if you run as a module:  python3 -m src.main
from src.bridge import send_imessage_to_chat
from src.assistant import generate_reply

# ---- single-instance lock ----
LOCK_PATH = "/tmp/kurama.lock"
lock_file = open(LOCK_PATH, "w")
try:
    fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
except OSError:
    print("Another Kurama instance is already running. Exiting.")
    sys.exit(0)
# ------------------------------

# ---- load config ----
CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "config.json"
with open(CONFIG_PATH) as f:
    CFG = json.load(f)

DB_PATH = CFG["db_path"]
SELF_HANDLE = CFG["self_handle"]

def get_latest_incoming_from_self(last_rowid: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT
            message.ROWID,
            handle.id,
            COALESCE(message.text, ''),
            chat.guid
        FROM message
        JOIN handle ON message.handle_id = handle.ROWID
        JOIN chat_message_join cmj ON cmj.message_id = message.ROWID
        JOIN chat ON chat.ROWID = cmj.chat_id
        WHERE message.is_from_me = 0
        ORDER BY message.ROWID DESC
        LIMIT 1;
    """)
    row = cur.fetchone()
    conn.close()
    if row and int(row[0]) > int(last_rowid):
        return row  # (rowid, sender_handle, text, chat_guid)
    return None


def main():
    print("👀 Assistant loop starting…")
    last_seen = 0

    while True:
        row = get_latest_incoming_from_self(last_seen)
        if row:
            rowid, sender, text, chat_guid = row
            print(f"📩 New message from {sender}: {text!r} (chat={chat_guid})")

            msg = (text or "").strip()
            if msg:
                # generate a reply and send it back to the same chat thread
                reply = generate_reply(msg)
                send_imessage_to_chat(chat_guid, reply)
                print(f"↩️ Replied: {reply}")

            # always advance so we don't reprocess the same message
            last_seen = int(rowid)

        time.sleep(2)

if __name__ == "__main__":
    main()

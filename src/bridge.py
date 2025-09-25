import sqlite3
import json
from pathlib import Path
import subprocess


def latest_message():
    # resolve path to config relative to repo root
    config_path = Path(__file__).resolve().parent.parent / "config" / "config.json"
    with open(config_path) as f:
        cfg = json.load(f)
    db_path = cfg["db_path"]

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
        SELECT message.ROWID, handle.id, message.text
        FROM message
        JOIN handle ON message.handle_id = handle.ROWID
        WHERE message.is_from_me = 0
        ORDER BY message.ROWID DESC
        LIMIT 1;
    """)
    row = cur.fetchone()
    conn.close()
    return row

def _escape_applescript(s: str) -> str:
    # Ensure we pass a safe literal AppleScript string
    if s is None:
        s = ""
    s = str(s)
    # Escape backslashes first, then quotes; make newlines literal \n
    s = s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return s

def send_imessage(handle: str, text: str) -> None:
    """
    Send an iMessage to a given handle (phone number or iCloud email).
    """
    safe = _escape_applescript(text)

    # Debug so we can see exactly what we're sending
    print(f"DEBUG send_imessage len={len(text) if text is not None else 0} raw={repr(text)}")
    print(f"DEBUG send_imessage safe={repr(safe)}")

    script = f'''
    tell application "Messages"
        set targetService to 1st service whose service type = iMessage
        set theBuddy to buddy "{handle}" of targetService
        send "{safe}" to theBuddy
    end tell
    '''
    try:
        subprocess.run(["osascript", "-e", script], check=True)
        print(f"✅ Sent to {handle}: {text}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to send: {e}")

def _escape_applescript(text: str) -> str:
    """Escape quotes so AppleScript is safe."""
    return text.replace('"', '\\"')


def send_imessage_to_chat(chat_guid: str, text: str) -> None:
    """
    Send a message to a specific chat (thread) by GUID.
    This keeps replies in the exact same iMessage conversation.
    """
    safe = _escape_applescript(text)
    print(f"DEBUG send_to_chat guid={chat_guid!r} text={safe!r}")

    script = f'''
    tell application "Messages"
        set theChat to chat id "{chat_guid}"
        send "{safe}" to theChat
    end tell
    '''

    try:
        subprocess.run(["osascript", "-e", script], check=True)
        print(f"✅ Sent to chat {chat_guid}: {text}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to send to chat {chat_guid}: {e}")



if __name__ == "__main__":
    print(latest_message())

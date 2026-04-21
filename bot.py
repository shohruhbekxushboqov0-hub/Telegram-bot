import requests
import json

# =====================================================
# SHU YERNI TO'LDIRING
TELEGRAM_TOKEN = "8742392856:AAF06n5MsCdOdHFiJQv3CJW9QRwksm-_fFQ"
ANTHROPIC_KEY  = "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"  
# =====================================================

SYSTEM = "Sen Shohruh nomidan javob beruvchi yordamchisan. O'zbek tilida qisqa va samimiy javob ber."

histories = {}
offset = 0

def claude(uid, text):
    if uid not in histories:
        histories[uid] = []
    histories[uid].append({"role": "user", "content": text})
    if len(histories[uid]) > 20:
        histories[uid] = histories[uid][-20:]
    r = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": ANTHROPIC_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        },
        json={
            "model": "claude-haiku-4-5-20251001",
            "max_tokens": 512,
            "system": SYSTEM,
            "messages": histories[uid]
        }
    )
    reply = r.json()["content"][0]["text"]
    histories[uid].append({"role": "assistant", "content": reply})
    return reply

def send(chat_id, text):
    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        json={"chat_id": chat_id, "text": text}
    )

def get_updates():
    global offset
    r = requests.get(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates",
        params={"offset": offset, "timeout": 30},
        timeout=35
    )
    return r.json().get("result", [])

print("Bot ishga tushdi!")
while True:
    try:
        updates = get_updates()
        for u in updates:
            offset = u["update_id"] + 1
            msg = u.get("message", {})
            text = msg.get("text", "")
            chat_id = msg.get("chat", {}).get("id")
            if not text or not chat_id:
                continue
            if text == "/start":
                send(chat_id, "Salom! Men Shohruh ning AI yordamchisiman. Savol bering!")
            elif text == "/clear":
                histories[chat_id] = []
                send(chat_id, "Suhbat tozalandi!")
            else:
                send(chat_id, claude(chat_id, text))
    except Exception as e:
        print("Xato:", e)

import os, time, requests
from decimal import Decimal
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("POLYSCAN_API_KEY")
WEBHOOK = os.getenv("DISCORD_WEBHOOK")
ADDR = os.getenv("WATCH_ADDRESS", "").lower().strip()

BASE = "https://api.polygonscan.com/api"
HEADERS = {"User-Agent": "polyscan-monitor/1.1"}

last_seen = {"native": None, "erc20": None}

def discord(msg: str):
    try:
        requests.post(WEBHOOK, json={"content": msg}, timeout=10)
    except Exception as e:
        print("discord error:", e)

def _fetch(params, label):
    try:
        r = requests.get(BASE, params=params, headers=HEADERS, timeout=20)
        j = r.json()
    except Exception as e:
        print(f"{label} fetch/json error:", e)
        return []

    status = str(j.get("status", ""))
    result = j.get("result", [])

    # אם קיבלנו טקסט במקום רשימה → אל תקרוס
    if not isinstance(result, list):
        txt = str(result)
        if "Max rate limit" in txt or "rate limit" in txt.lower():
            print(f"{label}: rate limited; backing off…")
            time.sleep(2.5)
            return []
        if "No transactions found" in txt:
            return []
        # תשובה לא צפויה
        print(f"{label}: unexpected result type:", txt[:120])
        return []

    return result

def get_native_txs():
    params = {
        "module": "account", "action": "txlist",
        "address": ADDR, "startblock": 0, "endblock": 99999999,
        "page": 1, "offset": 20, "sort": "desc", "apikey": API_KEY
    }
    return _fetch(params, "native")

def get_erc20_txs():
    params = {
        "module": "account", "action": "tokentx",
        "address": ADDR, "startblock": 0, "endblock": 99999999,
        "page": 1, "offset": 50, "sort": "desc", "apikey": API_KEY
    }
    return _fetch(params, "erc20")

def fmt_amount(value, decimals):
    try:
        q = Decimal(10) ** int(decimals)
        return (Decimal(value) / q).normalize()
    except Exception:
        return Decimal(0)

def short(addr):
    if not addr: return "-"
    a = addr if isinstance(addr, str) else str(addr)
    return a[:6] + "…" + a[-4:]

def tx_link(hash_):
    return f"https://polygonscan.com/tx/{hash_}"

def handle_native(txs):
    global last_seen
    if not txs: return

    # init pointer first run
    if last_seen["native"] is None:
        last_seen["native"] = txs[0].get("hash")
        return

    for tx in txs:
        h = tx.get("hash")
        if h == last_seen["native"]:
            break

        to = (tx.get("to") or "").lower()
        frm = (tx.get("from") or "").lower()
        direction = "IN ⬅️" if to == ADDR else "OUT ➡️"
        val = fmt_amount(tx.get("value", "0"), 18)
        msg = (
            f"**Transfer (MATIC)** {direction}\n"
            f"💸 {val} MATIC\n"
            f"From: `{short(frm)}`\n"
            f"To: `{short(to)}`\n"
            f"🔗 {tx_link(h)}"
        )
        discord(msg)

    last_seen["native"] = txs[0].get("hash")

def handle_erc20(txs):
    global last_seen
    if not txs: return

    if last_seen["erc20"] is None:
        last_seen["erc20"] = txs[0].get("hash")
        return

    for tx in txs:
        h = tx.get("hash")
        if h == last_seen["erc20"]:
            break

        to = (tx.get("to") or "").lower()
        frm = (tx.get("from") or "").lower()
        direction = "IN ⬅️" if to == ADDR else "OUT ➡️"
        sym = tx.get("tokenSymbol") or "TOKEN"
        val = fmt_amount(tx.get("value", "0"), tx.get("tokenDecimal", 18))
        msg = (
            f"**Transfer ({sym})** {direction}\n"
            f"💰 {val} {sym}\n"
            f"From: `{short(frm)}`\n"
            f"To: `{short(to)}`\n"
            f"🔗 {tx_link(h)}"
        )
        discord(msg)

    last_seen["erc20"] = txs[0].get("hash")

def main():
    if not API_KEY or not WEBHOOK or not ADDR:
        print("Missing env: POLYSCAN_API_KEY / DISCORD_WEBHOOK / WATCH_ADDRESS")
        return
    print("Monitoring:", ADDR)
    while True:
        try:
            handle_native(get_native_txs())
            handle_erc20(get_erc20_txs())
        except Exception as e:
            print("loop error:", e)
        time.sleep(5)

if __name__ == "__main__":
    main()

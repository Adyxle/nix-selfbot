"""
_store.py  -  shared helpers for the new cogs.

Files that start with "_" are NOT loaded as cogs by your main.py (it skips them),
but other cogs can import them:   from cogs._store import load, save, reply

What's in here:
  load(name, default)   read  <name>.json   (returns default if missing)
  save(name, data)      write <name>.json
  get_json(url, ...)    async web request that returns parsed JSON
  post_webhook(url, t)  send text to a Discord webhook (YOUR own webhook)
  parse_duration("1h30m") -> seconds
  reply(ctx, title, lines)  delete your command + send a boxed answer (uses _style.box)
"""
import json
import re
import aiohttp
from cogs._style import box

HEADERS = {"User-Agent": "Mozilla/5.0"}
TIMEOUT = aiohttp.ClientTimeout(total=10)


# ---------- tiny JSON "database" ----------
def load(name, default):
    try:
        with open(f"{name}.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save(name, data):
    with open(f"{name}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# ---------- web ----------
async def get_json(url, params=None, headers=None, method="GET", body=None):
    h = {**HEADERS, **(headers or {})}
    async with aiohttp.ClientSession(headers=h, timeout=TIMEOUT) as s:
        async with s.request(method, url, params=params, json=body) as r:
            r.raise_for_status()
            return await r.json(content_type=None)


async def get_text(url, params=None):
    async with aiohttp.ClientSession(headers=HEADERS, timeout=TIMEOUT) as s:
        async with s.get(url, params=params) as r:
            r.raise_for_status()
            return await r.text()


def valid_webhook(url):
    return bool(re.match(r"^https://(discord|discordapp)\.com/api/webhooks/\d+/[\w-]+/?$", (url or "").strip()))


async def post_webhook(url, text):
    if not url:
        print("[_store] post_webhook called with no URL set")
        return False
    try:
        async with aiohttp.ClientSession(timeout=TIMEOUT) as s:
            async with s.post(url.strip(), json={"content": str(text)[:1900]}) as r:
                if r.status >= 300:
                    body = await r.text()
                    print(f"[_store] webhook failed: status={r.status} body={body}")
                return r.status < 300
    except Exception as e:
        print(f"[_store] webhook exception: {e}")
        return False


# ---------- misc ----------
def parse_duration(text):
    """'1h30m' -> 5400 seconds. Returns None if it can't be understood."""
    parts = re.findall(r"(\d+)\s*([smhd])", (text or "").lower())
    if not parts:
        return None
    mult = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    return sum(int(n) * mult[u] for n, u in parts)


async def reply(ctx, title, lines, kind="info", delete_after=25, command=None):
    """Delete the command message, then send a boxed result that disappears later."""
    try:
        await ctx.message.delete()
    except Exception:
        pass
    return await ctx.send(box(title, lines, kind=kind, command=command), delete_after=delete_after)


async def plain(ctx, text, keep=True, delete_after=None):
    """Delete the command message and send plain text (good for lines people copy)."""
    try:
        await ctx.message.delete()
    except Exception:
        pass
    return await ctx.send(text, delete_after=None if keep else delete_after)

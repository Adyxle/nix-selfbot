r"""
_style.py  -  the NixWil look, in one place.

Every styled message in the bot goes through box(). Change things here and the
whole bot changes (autostyle.py wraps old cogs' plain messages in it too).

All emoji below are standard Unicode emoji, so they render for every user on
every device with no server membership or Nitro required.
"""
import re
from collections import OrderedDict

from cogs import _settings as _cfg
from cogs._settings import watermark_for

BRAND = "nixwil"

EMOJI = {
    "crown": "\U0001F451",      # 👑
    "success": "\u2705",        # ✅
    "error": "\u274C",          # ❌
    "info": "\u2139\uFE0F",     # ℹ️
    "warning": "\u26A0\uFE0F",  # ⚠️
    "loading": "\u23F3",        # ⏳
    "arrow": "\u27A1\uFE0F",    # ➡️
    "dot": "\u2022",            # •
    "on": "\U0001F7E2",         # 🟢
    "off": "\U0001F534",        # 🔴
    "premium": "\U0001F48E",    # 💎
    "money": "\U0001F4B0",      # 💰
    "ping": "\U0001F3D3",       # 🏓
}

# Emoji for each module in .help  (key = cog class name in lowercase)
SECTION_EMOJI = {
    "admin": "\U0001F6E1\uFE0F",     # 🛡️
    "afk": "\U0001F4A4",             # 💤
    "automsg": "\U0001F4E8",         # 📨
    "ars": "\U0001F4AC",             # 💬
    "crypto": "\U0001FA99",          # 🪙
    "dump": "\U0001F4E6",            # 📦
    "fun": "\U0001F389",             # 🎉
    "funextras": "\U0001F602",       # 😂
    "help": "\U0001F4D6",            # 📖
    "hentai": "\U0001F51E",          # 🔞
    "image": "\U0001F5BC\uFE0F",     # 🖼️
    "info": "\u2139\uFE0F",          # ℹ️
    "purge": "\U0001F525",           # 🔥
    "statusrotator": "\U0001F7E2",   # 🟢
    "svm": "\U0001F4EC",             # 📬
    "syntaxhelper": "\U0001F4CB",    # 📋
    "utility": "\U0001F6E0\uFE0F",   # 🛠️
    "vc": "\U0001F3B5",              # 🎵
    "vcextra": "\U0001F4DE",         # 📞
    "vouch": "\u2B50",               # ⭐
    "snipe": "\U0001F50D",           # 🔍
    "remind": "\u23F0",              # ⏰
    "alerts": "\U0001F514",          # 🔔
    "txcheck": "\U0001F4B3",         # 💳
    "paywatch": "\U0001F4B5",        # 💵
    "roles": "\U0001F3AD",           # 🎭
    "tools": "\U0001F527",           # 🔧
    "ai": "\U0001F916",              # 🤖
    "channels": "\U0001F4CB",        # 📋
    "shop": "\U0001F6D2",            # 🛒
    "members": "\U0001F465",         # 👥
    "support": "\U0001F198",         # 🆘
    "staff": "\U0001F46E",           # 👮
    "security": "\U0001F512",        # 🔒
    "qr": "\U0001F533",              # 🔳
}


def section_emoji(name):
    return SECTION_EMOJI.get(str(name).lower(), EMOJI["arrow"])


# ---------------------------------------------------------------------------
# Fonts: Discord can't change fonts, but unicode has look-alike alphabets.
# small() turns  "afk help"  into  "\u1d00\ua730\u1d0b \u029c\u1d07\u029f\u1d18".
# ---------------------------------------------------------------------------
_NORMAL = "abcdefghijklmnopqrstuvwxyz"
_SMALL = "\u1d00\u0299\u1d04\u1d05\u1d07\ua730\u0262\u029c\u026a\u1d0a\u1d0b\u029f\u1d0d\u0274\u1d0f\u1d18\u01eb\u0280\ua731\u1d1b\u1d1c\u1d20\u1d21x\u028f\u1d22"
assert len(_NORMAL) == len(_SMALL) == 26
_SMALL_MAP = str.maketrans(_NORMAL, _SMALL)


_KEEP = re.compile(r"(<a?:\w+:\d+>|`[^`\n]*`|https?://\S+)|([A-Za-z]+)")


def small(text):
    """small-caps font. Letters only; custom emojis, `code` and links stay untouched."""
    def _sub(m):
        if m.group(1):
            return m.group(1)
        return m.group(2).lower().translate(_SMALL_MAP)
    return _KEEP.sub(_sub, str(text))


FOOT_BRAND = small(BRAND)


# ---------------------------------------------------------------------------
# Tracking messages the BOT sent (so cogs like afk.py can tell them apart from
# messages you typed yourself - on a selfbot both come from the same account).
# ---------------------------------------------------------------------------
_SENT_IDS = OrderedDict()


def mark_sent(msg):
    """Remember that the bot sent this message (keeps only the last 500)."""
    mid = getattr(msg, "id", None)
    if mid is None:
        return
    _SENT_IDS[mid] = True
    while len(_SENT_IDS) > 500:
        _SENT_IDS.popitem(last=False)


def is_bot_sent(message_id):
    return message_id in _SENT_IDS


def is_noir_text(content):
    """True if this text is a styled NixWil message (it carries the footer)."""
    return bool(content) and f"-# {EMOJI['crown']} {FOOT_BRAND}" in content


# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# autocopy(): wraps important values in `backticks` so they're easy to select/copy.
#   - numbers with 6+ digits (phone numbers, IDs), emails, IP addresses
#   - long letter+digit strings 26-64 chars (crypto addresses, tx hashes, tokens)
# It skips anything already in `code`/code blocks, links, and <emojis/@mentions>.
# ---------------------------------------------------------------------------
_COPY = re.compile(
    r"(```[\s\S]*?```|`[^`\n]*`|<[^>\n]+>|https?://\S+)"       # skip: code, <emoji/@mention>, links
    r"|(?<![\w.])("
    r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+"                          # email
    r"|\d{1,3}(?:\.\d{1,3}){3}"                              # IPv4
    r"|\+\d{1,3}[ -]\d{6,}"                                  # +977 9812345678
    r"|\+?\d{6,}"                                            # 6+ digit numbers / IDs
    r"|(?=[A-Za-z0-9]*\d)[A-Za-z0-9]{26,64}"                 # addresses, hashes, tokens
    r")(?!\w|\.\d)"
)


def autocopy(text):
    def _sub(m):
        if m.group(1):
            return m.group(1)
        return f"`{m.group(2)}`"
    return _COPY.sub(_sub, str(text))


class Styled(str):
    """A message that box() already styled (autostyle.py leaves these alone)."""


def box(title, lines, kind="info", theme=None, command=None, big=False, watermark=None, copy=None):
    """
    Build a minimalist styled Discord message (no # headers).

    title     : heading text (only shown on multi-line messages, small-caps font)
    lines     : a string or list of strings (one per line)
    kind      : "info" | "success" | "error" | "warning"  (picks the emoji)
    big       : True -> crown icon + title always shown (used for menus)
    command   : shown in the footer as `code`; also used to look up _settings.py
    watermark : True/False to force the footer on/off; None -> use _settings.py
    copy      : True/False to force auto-copy formatting on/off; None -> use _settings.py
    `theme` is accepted only so older cogs that pass it keep working.

    ONE-LINE message   ->  > (icon) text
                           -# (crown) ɴɪxᴡɪʟ • `cmd`

    MULTI-LINE message ->  > (icon) **ᴛɪᴛʟᴇ**
                           > line
                           -# (crown) ɴɪxᴡɪʟ • `cmd`

    Lines that already start with ">" are stripped first (no "> >"), and old
    "# / ## / ###" headers are turned into **bold**.
    TIP: wrap values in `backticks` inside your text to get the code look.
    """
    mark = EMOJI["crown"] if big else EMOJI.get(kind, EMOJI["info"])

    if watermark is None:
        watermark = watermark_for(command)

    if copy is None:
        copy = getattr(_cfg, "AUTO_COPY", True) and (command or "") not in getattr(_cfg, "NO_AUTO_COPY", ())

    text = lines if isinstance(lines, str) else "\n".join(str(l) for l in lines)
    if copy:
        text = autocopy(text)
    raw = text.split("\n")

    raw = [re.sub(r"^(?:>\s?)+", "", l) for l in raw]
    raw = [re.sub(r"^#{1,3}\s+(.*)$", r"**\1**", l) for l in raw]
    while raw and not raw[0].strip():
        raw.pop(0)
    while raw and not raw[-1].strip():
        raw.pop()

    foot = ""
    if watermark:
        foot = f"-# {EMOJI['crown']} {FOOT_BRAND}" + (f" {EMOJI['dot']} `{command}`" if command else "")

    if len(raw) <= 1 and not big:
        body = f"> {mark} {raw[0] if raw else ''}".rstrip()
    else:
        head = f"> {mark} **{small(title)}**"
        rows = "\n".join(f"> {l}" if l.strip() else "> \u200b" for l in raw)
        body = f"{head}\n{rows}" if rows else head

    out = body + (f"\n{foot}" if foot else "")
    if len(out) > 1990:
        out = out[:1980].rstrip() + "…"
    return Styled(out)

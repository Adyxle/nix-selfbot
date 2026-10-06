"""
_settings.py  -  YOUR control panel. Edit this file only.

For every command reply the bot looks up, in this order (first match wins):
    1) the COMMAND name        (DELAYS / WATERMARK)
    2) the MODULE (cog) name   (MODULE_DELAYS / MODULE_WATERMARK)
    3) the SECTION it belongs to  (SECTION_DELAYS / SECTION_WATERMARK)
    4) the DEFAULT below
Names are lowercase. Command name = the main name, not an alias (use ,help <cmd>).
Module name = the same names ,help lists (e.g. "afk", "hentai"). Underscores don't matter.
Section name = moderation / automation / utility / entertainment (edit SECTIONS to change them).
"""

# ---------------------------------------------------------------------------
# SECTIONS  (which modules live in which ,help section)
# ,help reads this too - move a module here and it moves in ,help as well.
# ---------------------------------------------------------------------------
SECTIONS = {
    "moderation": ["admin", "purge", "roles", "dump", "wizz", "nuke"],
    "automation": ["afk", "alerts", "automsg", "ars", "remind", "statusrotator", "svm"],
    "utility": ["utility", "tools", "info", "image", "crypto", "nepal", "txcheck", "paywatch"],
    "entertainment": ["fun", "funextras", "ai", "hentai", "vc", "vcextra"],
}

# Menu name -> real cog / file name, for names that don't match exactly.
MODULE_ALIASES = {
    "nsfw": "hentai",
    "automsg": "automessage",
    "ars": "autoresponder",
    "utility": "utiltity",
}

# ---------------------------------------------------------------------------
# AUTO-DELETE  (seconds the reply stays before it deletes itself)
#   a number  -> delete after that many seconds
#   None      -> NEVER delete
# ---------------------------------------------------------------------------
DEFAULT_DELAY = 6

DELAYS = {
    "help": 40,
    "allcmds": 30,
    "afk": 8,
    "afk_report": 90,     # the "welcome back + who pinged you" report in afk.py
    # "ping": 3,
    # "userinfo": None,   # None = stays forever
}

MODULE_DELAYS = {
    "hentai": None,
    # "dump": 30,
}

SECTION_DELAYS = {
    # "entertainment": 15,   # every module in the section
}

# ---------------------------------------------------------------------------
# NOIR WATERMARK  (the small  👑 ɴᴏɪʀ • `cmd`  footer line)
#   True  -> show it        False -> hide it
# ---------------------------------------------------------------------------
DEFAULT_WATERMARK = True

WATERMARK = {
    # "ping": False,
    # "help": True,
}

MODULE_WATERMARK = {
    # "info": False,
}

SECTION_WATERMARK = {
    # "entertainment": False,   # no watermark on fun, funextras, ai, hentai, vc, vcextra
    # "moderation": False,
}

# ---------------------------------------------------------------------------
# RAW (no styling at all)
# Commands/modules/sections listed here have their ctx.send text sent EXACTLY as
# written - use this for anything that must stay plain, like commands that repeat
# text you give them.
# ---------------------------------------------------------------------------
RAW_COMMANDS = {"say", "echo"}
RAW_MODULES = set()
RAW_SECTIONS = set()

# ---------------------------------------------------------------------------
# AUTO-COPY: wraps long numbers (6+ digits), emails, IP addresses and crypto
# addresses/hashes in `backticks` so they're easy to select and copy.
# Works in EVERY styled message (box). True = on, False = off.
# NO_AUTO_COPY = commands where it should NOT happen.
# ---------------------------------------------------------------------------
AUTO_COPY = True
NO_AUTO_COPY = set()


# ---------------------------------------------------------------------------
# lookup helpers (you don't need to touch these)
# ---------------------------------------------------------------------------
BOT = None   # autostyle.py sets this when the bot starts


def _norm(x):
    return str(x).lower().replace("_", "").replace("-", "").replace(" ", "")


def _lookup(table, key):
    if key is None:
        return False, None
    nk = _norm(key)
    for k, v in table.items():
        if _norm(k) == nk:
            return True, v
    return False, None


def _modules(command, module):
    """List of names the command's module goes by (class name + file name)."""
    if module is not None:
        return [module] if isinstance(module, str) else list(module)
    if BOT is None or not command:
        return []
    try:
        cmd = BOT.get_command(str(command).split()[0])
        cog = getattr(cmd, "cog", None)
        if cog:
            return [cog.qualified_name, cog.__module__.split(".")[-1]]
    except Exception:
        pass
    return []


def _section_of(mods):
    wanted = {_norm(m) for m in mods}
    for section, names in SECTIONS.items():
        for n in names:
            if {_norm(n), _norm(MODULE_ALIASES.get(n, n))} & wanted:
                return section
    return None


def _pick(by_command, by_module, by_section, default, command, module):
    found, val = _lookup(by_command, command)
    if found:
        return val
    mods = _modules(command, module)
    for m in mods:
        found, val = _lookup(by_module, m)
        if found:
            return val
    section = _section_of(mods)
    found, val = _lookup(by_section, section)
    if found:
        return val
    return default


def delay_for(command=None, module=None):
    return _pick(DELAYS, MODULE_DELAYS, SECTION_DELAYS, DEFAULT_DELAY, command, module)


def watermark_for(command=None, module=None):
    return _pick(WATERMARK, MODULE_WATERMARK, SECTION_WATERMARK, DEFAULT_WATERMARK, command, module)


def is_raw(command=None, module=None):
    if command and _norm(command) in {_norm(c) for c in RAW_COMMANDS}:
        return True
    mods = _modules(command, module)
    if any(_norm(m) in {_norm(r) for r in RAW_MODULES} for m in mods):
        return True
    return _section_of(mods) in RAW_SECTIONS


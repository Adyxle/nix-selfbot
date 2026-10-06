"""
Central registry of module descriptions for ,help <module>.

Keys are lowercase cog class names (matches cog_name.lower() in help.py).
"""

MODULE_DESCRIPTIONS = {
    "admin": "Server moderation — bans, kicks, nickname locks, channel reset.",
    "afk": "Tracks who pings or replies to you while away and reports it when you return.",
    "ai": "Chat with an AI assistant, with a configurable system prompt, per channel.",
    "alerts": "Webhook-based alerts for DMs, mentions, keywords, and role pings.",
    "automsg": "Schedules a one-off or repeating message in a channel.",
    "ars": "Auto-replies to messages matching configured trigger words.",
    "crypto": "Crypto balance lookups, live prices, and conversions.",
    "dump": "Bulk-export attachments, text, emojis, or avatars from a channel or guild.",
    "fun": "Lighthearted commands — spam, mass react, animated status.",
    "funextras": "Novelty commands — memes, animal pics, jokes, 8ball, coinflip, dice.",
    "help": "Custom help command — lists modules and command syntax.",
    "hentai": "NSFW adult content commands — anime and real-life adult media lookup.",
    "image": "Set your own avatar from a URL, or set your account password for avatar changes.",
    "info": "Lookup commands — avatars, user info, selfbot stats, ping, IP geolocation, IDs.",
    "nepal": "Khalti payment info, QR code, and NPR/USD/crypto conversion rates.",
    "paywatch": "Watch crypto addresses and get a webhook alert on incoming payments.",
    "purge": "Deletes your own last N messages in this channel.",
    "remind": "Set, list, and remove personal reminders.",
    "roles": "Role and channel-visibility management — create roles, hide channels, ban by ID.",
    "snipe": "Shows the last deleted or edited message in a channel.",
    "statusrotator": "Rotates your custom Discord status through a list of messages.",
    "svm": "Configurable auto-repeating messages with rotating presets, per channel.",
    "syntaxhelper": "Shows the correct syntax automatically when you use a command wrong.",
    "tools": "Utility lookups — QR codes, translation, weather, Minecraft server status, link checking.",
    "txcheck": "Look up a BTC/LTC/DOGE or TRON transaction by ID.",
    "utility": "General tools — ASCII art, server scans, nickname looping, server cloning, status.",
    "vc": "Voice channel moderation — 24/7 presence, kick, mute, move all.",
    "vcextra": "More voice channel controls — join, leave, deafen, move one user, set limits.",
    "vouch": "Post formatted vouch messages for completed trades.",
    "wizz": "Server destruction suite — nukechannels, randomban, massban, massunban, and massdm.",
}


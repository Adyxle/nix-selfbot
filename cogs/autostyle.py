"""
autostyle.py  -  makes EVERY plain ctx.send(...) in every cog use the Noir look.

How it works: we replace commands.Context.send with our own function. Plain text
is wrapped with box() from _style.py. Delay + watermark come from _settings.py.

It leaves alone: links (so previews work), files/embeds, messages that are already
styled, and anything you put in RAW_COMMANDS / RAW_MODULES in _settings.py.
Old-style "## Title" first lines become the box title. Long output is split into
several boxes instead of being cut off.

It also remembers the ID of every message the bot sends (ctx.send AND
channel.send) so afk.py can tell "the bot said this" from "you typed this".
"""
import re

import discord
import discord.abc
from discord.ext import commands

from cogs import _settings as cfg
from cogs._style import Styled, autocopy, box, is_noir_text, mark_sent

_original_send = commands.Context.send
_original_messageable_send = discord.abc.Messageable.send

ERROR_WORDS = ("error", "failed", "invalid", "not found", "missing", "can't", "cannot",
               "couldn't", "incorrect", "no permission", "don't have", "not allowed")
SUCCESS_WORDS = ("added", "saved", "deleted", "set", "stopped", "scheduled", "kicked", "banned",
                 "unbanned", "updated", "cleared", "removed", "created", "done", "enabled",
                 "disabled", "started")

HEADER = re.compile(r"^#{1,3}\s+(.*)$")


def _guess_kind(content):
    low = content.lower()
    if any(w in low for w in ERROR_WORDS):
        return "error"
    if any(w in low for w in SUCCESS_WORDS):
        return "success"
    return "info"


def _chunks(lines, limit=1700):
    """Split lines into groups that each fit in one Discord message."""
    chunks, cur, size = [], [], 0
    for line in lines:
        pieces = [line[i:i + limit] for i in range(0, len(line), limit)] or [""]
        for piece in pieces:
            if cur and size + len(piece) + 1 > limit:
                chunks.append(cur)
                cur, size = [], 0
            cur.append(piece)
            size += len(piece) + 1
    if cur:
        chunks.append(cur)
    return chunks or [[""]]


async def _styled_send(self, content=None, **kwargs):
    cmd = self.command.qualified_name.lower() if self.command else None
    cog = self.command.cog if self.command else None
    module = [cog.qualified_name, cog.__module__.split(".")[-1]] if cog else None
    kwargs.setdefault("delete_after", cfg.delay_for(cmd, module))

    skip = (
        not isinstance(content, str)
        or not content.strip()
        or kwargs.get("embed") is not None
        or kwargs.get("file") is not None
        or kwargs.get("files") is not None
        or content.startswith("http")
        or isinstance(content, Styled)
        or is_noir_text(content)
        or cfg.is_raw(cmd, module)
    )
    if skip:
        msg = await _original_send(self, content, **kwargs)
        mark_sent(msg)
        return msg

    if getattr(cfg, "AUTO_COPY", True) and cmd not in getattr(cfg, "NO_AUTO_COPY", ()):
        content = autocopy(content)

    lines = content.split("\n")
    title, big = (cmd or "noir"), False
    m = HEADER.match(lines[0])
    if m and len(lines) > 1:            # old "## Title" style -> use it as the box title
        title, big, lines = m.group(1), True, lines[1:]

    kind = _guess_kind(content)
    watermark = cfg.watermark_for(cmd, module)

    msg = None
    for part in _chunks(lines):
        msg = await _original_send(
            self,
            box(title, part, kind=kind, command=cmd, big=big, watermark=watermark),
            **kwargs,
        )
        mark_sent(msg)
    return msg


async def _recording_send(self, *args, **kwargs):
    """Plain channel.send / user.send: just remember the message ID."""
    msg = await _original_messageable_send(self, *args, **kwargs)
    mark_sent(msg)
    return msg


async def setup(bot):
    cfg.BOT = bot
    if not getattr(commands.Context, "_noir_styled", False):
        commands.Context.send = _styled_send
        commands.Context._noir_styled = True
    if not getattr(discord.abc.Messageable, "_noir_recording", False):
        discord.abc.Messageable.send = _recording_send
        discord.abc.Messageable._noir_recording = True


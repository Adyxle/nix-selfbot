import discord
from discord.ext import commands

from main import infected
from cogs._style import box, small, section_emoji
from cogs import _settings as cfg
from cogs._settings import watermark_for
from cogs._module_descriptions import MODULE_DESCRIPTIONS
from cogs._command_descriptions import COMMAND_DESCRIPTIONS

# 3-tier grouping:  ,help  ->  ,help <section>  ->  ,help <module>  ->  ,help <command>
# Which modules are in which section is set in _settings.py (SECTIONS).
GROUPS = {
    "moderation": {
        "emoji": "\U0001F6E1\uFE0F",     # 🛡️
        "cogs": cfg.SECTIONS["moderation"],
        "desc": "Server defense, moderation, and data logging cogs.",
        "short": "Server control & logging",
    },
    "automation": {
        "emoji": "\u2699\uFE0F",         # ⚙️
        "cogs": cfg.SECTIONS["automation"],
        "desc": "Automated reactions, status rotators, away tracking, and alerts.",
        "short": "AFK, alerts & auto-replies",
    },
    "utility": {
        "emoji": "\U0001F6E0\uFE0F",     # 🛠️
        "cogs": cfg.SECTIONS["utility"],
        "desc": "General utility tools, information checkers, and geo lookups.",
        "short": "Tools, info & crypto",
    },
    "entertainment": {
        "emoji": "\U0001F389",           # 🎉
        "cogs": cfg.SECTIONS["entertainment"],
        "desc": "Fun text interactions, adult media endpoints, and voice controls.",
        "short": "Fun, media & voice",
    },
}

DIV = "---------"

# ---- look settings (change these) ----
SHOW_SECTION_DESC = True   # ,help            : True = one short description line under each section
SHOW_INTRO = False         # True = show the italic one-line description at the top of section/module pages
SHOW_MODULE_DESC = False   # ,help <section>  : True = show a short description after each module
COMMAND_DESC_MAX = 0       # ,help <module>   : 0 = command names only (cleanest)
                           #                    40 = names + descriptions cut to 40 characters

# Menu name -> real cog / file name (edit in _settings.py)
MODULE_ALIASES = cfg.MODULE_ALIASES


def _short(text, n):
    """Cut text to about n characters at a word boundary, adding an ellipsis."""
    text = " ".join(str(text).split())
    if len(text) <= n:
        return text
    return text[:n].rsplit(" ", 1)[0].rstrip(",;:-—") + "…"


def _chunks(lines, limit=1600):
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


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ---- helpers -----------------------------------------------------------
    def _find_cog(self, name):
        """Find a cog by class name OR file name, case-insensitive, with aliases."""
        name = MODULE_ALIASES.get(name.lower(), name.lower())
        for cog in self.bot.cogs.values():
            file_name = cog.__module__.split(".")[-1].lower()
            if name in (cog.qualified_name.lower(), file_name):
                return cog
        return None

    @staticmethod
    def _describe(cmd):
        """Description priority: set on the command itself, then the registry."""
        return (
            cmd.brief
            or cmd.description
            or COMMAND_DESCRIPTIONS.get(cmd.qualified_name.lower())
            or "No description provided."
        )

    async def _send(self, ctx, title, lines, kind="info", big=False, command="help"):
        """Send as one styled box, or several pages if it's too long."""
        wm = watermark_for("help")
        parts = _chunks(lines)
        for i, part in enumerate(parts, 1):
            t = f"{title} {i}/{len(parts)}" if len(parts) > 1 else title
            await ctx.send(
                box(t, part, kind=kind, big=big or len(parts) > 1, command=command, watermark=wm)
            )

    # ---- the command -------------------------------------------------------
    @commands.command(name="help", description="Shows all sections, a module's commands, or one command's syntax.")
    @infected()
    async def help_cmd(self, ctx, *, query: str = None):
        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass

        prefix = ctx.prefix
        lines = []

        # ─── TIER 1: ,help ───
        if query is None:
            for name, info in GROUPS.items():
                lines.append(f"{info['emoji']} **{small(name)}** • `{prefix}help {name}`")
                if SHOW_SECTION_DESC:
                    lines.append(f"*{info['short']}*")
                lines.append(DIV)
            lines.append(f"`{prefix}help <module>` • `{prefix}help <command>`")
            return await self._send(ctx, "nixwil self utility", lines, big=True)

        query_clean = query.lower().strip().replace(" ", "")

        # ─── TIER 2: ,help <section> ───
        if query_clean in GROUPS:
            info = GROUPS[query_clean]
            if SHOW_INTRO:
                lines.append(f"*{info['desc']}*")
                lines.append(DIV)
            for cog_name in info["cogs"]:
                cog = self._find_cog(cog_name)
                if not cog:
                    continue
                visible = [c for c in cog.get_commands() if not c.hidden]
                if not visible:
                    continue
                line = f"{section_emoji(cog_name)} **{small(cog_name)}** `{len(visible)}`"
                desc = MODULE_DESCRIPTIONS.get(cog_name.lower())
                if SHOW_MODULE_DESC and desc:
                    line += f" — {_short(desc, 40)}"
                lines.append(line)
            lines.append(DIV)
            lines.append(f"`{prefix}help <module>`")
            return await self._send(
                ctx, query_clean, lines, big=True, command=f"help {query_clean}"
            )

        # ─── TIER 3: ,help <module> ───
        found_cog = self._find_cog(query_clean)
        if found_cog:
            label = MODULE_ALIASES.get(query_clean, query_clean)
            mod_desc = MODULE_DESCRIPTIONS.get(query_clean, "")
            if SHOW_INTRO and mod_desc:
                lines.append(f"*{_short(mod_desc, 60)}*")
                lines.append(DIV)

            cog_cmds = sorted(
                (c for c in found_cog.get_commands() if not c.hidden),
                key=lambda c: c.name.lower(),
            )
            if COMMAND_DESC_MAX > 0:
                for cmd in cog_cmds:
                    lines.append(f"`{prefix}{cmd.name}` — {_short(self._describe(cmd), COMMAND_DESC_MAX)}")
            else:
                lines.append(" ".join(f"`{prefix}{c.name}`" for c in cog_cmds))
            lines.append(DIV)
            lines.append(f"`{prefix}help <command>`")
            return await self._send(
                ctx, label, lines, big=True, command=f"help {query_clean}"
            )

        # ─── TIER 4: ,help <command> ───
        found_cmd = self.bot.get_command(query.strip().lower())
        if found_cmd and not found_cmd.hidden:
            usage = found_cmd.usage or f"{prefix}{found_cmd.qualified_name} {found_cmd.signature}".strip()
            lines.append(f"`{usage}`")
            lines.append(self._describe(found_cmd))
            if found_cmd.aliases:
                lines.append("aliases: " + ", ".join(f"`{a}`" for a in found_cmd.aliases))
            return await self._send(ctx, found_cmd.name, lines, command="help")

        # ─── NOT FOUND ───
        return await self._send(
            ctx, "help",
            [f"`{query}` not found. Try `{prefix}help`."],
            kind="error",
        )


async def setup(bot):
    await bot.add_cog(Help(bot))

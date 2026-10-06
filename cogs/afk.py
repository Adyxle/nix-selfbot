import asyncio
import time
from datetime import datetime, timezone

import discord
from discord.ext import commands

from cogs._style import box, is_bot_sent, is_noir_text
from cogs._settings import delay_for


class AFK(commands.Cog):
    """Tracks who pings or replies to you while you're away and reports it when you return."""

    def __init__(self, bot):
        self.bot = bot
        self.afk_users = {}   # user_id -> {"reason": str, "since": float}
        self.ping_log = {}    # user_id -> list of ping records

    # ---- helper: send a boxed AFK message through any send function --------
    async def _say(self, send, text, kind="info", delete_after=None):
        await send(box("AFK", text, kind=kind, command="afk"), delete_after=delete_after)

    @commands.command(description="Set yourself as AFK with an optional reason.")
    async def afk(self, ctx, *, reason: str = "AFK"):
        """Set yourself as AFK. Usage: ,afk [reason]"""
        self.afk_users[ctx.author.id] = {
            "reason": reason,
            "since": time.time(),
        }
        self.ping_log[ctx.author.id] = []

        await self._say(ctx.send, f"You're now AFK: `{reason}`", "success", delay_for("afk"))

    @commands.command(aliases=["unafk", "back"], description="Clear your AFK status and see who pinged you while away.")
    async def afkoff(self, ctx):
        """Manually clear your AFK status and see who pinged you."""
        if ctx.author.id not in self.afk_users:
            await self._say(ctx.send, "You're not AFK.", "info", delay_for("afk"))
            return
        await self._clear_afk(ctx.author.id, ctx.send)

    async def _clear_afk(self, user_id, send):
        if user_id not in self.afk_users:
            return

        data = self.afk_users.pop(user_id)
        pings = self.ping_log.pop(user_id, [])

        duration = time.time() - data["since"]
        mins, secs = divmod(int(duration), 60)
        hrs, mins = divmod(mins, 60)
        duration_str = f"{hrs}h {mins}m {secs}s" if hrs else f"{mins}m {secs}s"

        if not pings:
            await self._say(
                send,
                f"Welcome back. You were AFK for `{duration_str}`. No pings while you were away.",
                "success", delay_for("afk"),
            )
            return

        lines = [f"Welcome back. You were AFK for `{duration_str}`."]
        lines.append(f"`{len(pings)}` ping(s) while you were away:\n")

        for i, p in enumerate(pings, 1):
            ts = p["time"].strftime("%Y-%m-%d %H:%M:%S UTC")
            lines.append(
                f"**{i}.** {p['author']} (`{p['author_id']}`)\n"
                f"   {p['guild']} \u2022 `#{p['channel']}` \u2022 `{ts}`\n"
                f"   {p['content']}\n"
            )

        full_report = "\n".join(lines)

        # Discord's 2000 char limit (box adds a header/footer) - split into chunks
        chunks = [full_report[i:i + 1700] for i in range(0, len(full_report), 1700)]
        for chunk in chunks:
            await self._say(send, chunk, "info", delay_for("afk_report"))

    @commands.Cog.listener()
    async def on_message(self, message):
        me = self.bot.user.id

        # ---- messages from YOUR account (typed by you OR sent by the bot) ----
        if message.author.id == me:
            # 1) styled bot replies carry the noir footer - ignore instantly
            if is_noir_text(message.content) or is_bot_sent(message.id):
                return
            # 2) commands you typed (,afk ,help ...) are not "talking"
            ctx = await self.bot.get_context(message)
            if ctx.valid:
                return
            # 3) other plain bot sends: wait a moment so autostyle can record the ID
            await asyncio.sleep(1)
            if is_bot_sent(message.id):
                return
            # 4) this really is you typing -> come back from AFK
            if me in self.afk_users and message.content:
                await self._clear_afk(me, message.channel.send)
            return  # your own messages never count as pings

        if message.author.bot:
            return

        # ---- check if anyone AFK was pinged or replied to ----
        mentioned_ids = {u.id for u in message.mentions}

        # also catch replies even without an explicit @mention
        if message.reference and message.reference.resolved:
            resolved = message.reference.resolved
            if isinstance(resolved, discord.Message):
                mentioned_ids.add(resolved.author.id)

        for uid in mentioned_ids:
            if uid in self.afk_users and uid != message.author.id:
                record = {
                    "author": str(message.author),
                    "author_id": message.author.id,
                    "guild": message.guild.name if message.guild else "DM",
                    "channel": message.channel.name if hasattr(message.channel, "name") else "DM",
                    "content": message.content[:200] if message.content else "(no text content)",
                    "time": datetime.now(timezone.utc),
                }
                self.ping_log.setdefault(uid, []).append(record)

                reason = self.afk_users[uid]["reason"]
                who = self.bot.get_user(uid) or "that user"
                try:
                    await message.channel.send(
                        box("AFK", f"{message.author.mention} **{who}** is AFK: `{reason}`", kind="info", command="afk"),
                        delete_after=delay_for("afk"),
                    )
                except (discord.Forbidden, discord.HTTPException):
                    pass


async def setup(bot):
    await bot.add_cog(AFK(bot))


"""
remind.py  -  reminders that survive restarts.

LEARN: asyncio.sleep() waits without freezing the bot. Reminders are saved to
reminders.json so after a restart `cog_load` re-creates the waiting tasks.
Set a webhook with .setremindhook to get the ping privately; otherwise it posts
in the channel where you set it.
"""
import asyncio
import time
from discord.ext import commands
from main import infected
from cogs._store import load, save, reply, parse_duration, post_webhook, valid_webhook


class Remind(commands.Cog):
    """Reminders."""

    def __init__(self, bot):
        self.bot = bot
        self.tasks = {}

    async def cog_load(self):
        for r in load("reminders", []):
            self._schedule(r)

    async def cog_unload(self):
        for t in self.tasks.values():
            t.cancel()

    def _schedule(self, r):
        self.tasks[r["id"]] = asyncio.create_task(self._run(r))

    async def _run(self, r):
        try:
            await asyncio.sleep(max(0, r["due"] - time.time()))
        except asyncio.CancelledError:
            return
        text = f"Reminder: {r['text']}"
        hook = load("remind_hook", "")
        if not await post_webhook(hook, text):
            ch = self.bot.get_channel(r["channel_id"])
            if ch:
                try:
                    await ch.send(text)
                except Exception:
                    pass
        save("reminders", [x for x in load("reminders", []) if x["id"] != r["id"]])
        self.tasks.pop(r["id"], None)

    @commands.command(name="remind", brief="Set a reminder", usage=".remind <10m|2h|1d> <text>")
    @infected()
    async def remind(self, ctx, duration: str, *, text: str):
        secs = parse_duration(duration)
        if not secs:
            return await reply(ctx, "Remind", ["Use a time like 10m, 2h, 1d."], kind="error", delete_after=8)
        items = load("reminders", [])
        rid = max([x["id"] for x in items], default=0) + 1
        r = {"id": rid, "due": time.time() + secs, "text": text, "channel_id": ctx.channel.id}
        items.append(r)
        save("reminders", items)
        self._schedule(r)
        await reply(ctx, "Remind", [f"#{rid} in {duration}", text], kind="success", delete_after=10)

    @commands.command(name="reminders", brief="List reminders", usage=".reminders")
    @infected()
    async def reminders(self, ctx):
        items = load("reminders", [])
        lines = [f"#{r['id']} in {int((r['due'] - time.time()) // 60)}m - {r['text']}" for r in items]
        await reply(ctx, "Reminders", lines or ["None."])

    @commands.command(name="rmremind", brief="Remove a reminder", usage=".rmremind <id>")
    @infected()
    async def rmremind(self, ctx, rid: int):
        t = self.tasks.pop(rid, None)
        if t:
            t.cancel()
        save("reminders", [x for x in load("reminders", []) if x["id"] != rid])
        await reply(ctx, "Remind", [f"Removed #{rid}"], kind="success", delete_after=6)

    @commands.command(name="setremindhook", brief="Webhook for reminders", usage=".setremindhook <webhook>")
    @infected()
    async def setremindhook(self, ctx, url: str):
        if not valid_webhook(url):
            return await reply(ctx, "Remind", ["Not a valid webhook URL."], kind="error", delete_after=6)
        save("remind_hook", url)
        await reply(ctx, "Remind", ["Webhook saved."], kind="success", delete_after=6)


async def setup(bot):
    await bot.add_cog(Remind(bot))

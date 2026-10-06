"""
paywatch.py  -  get a webhook ping when a watched crypto address receives a new transaction.

LEARN: a background loop (asyncio task) checks each address every ~90 seconds.
The first check just remembers the latest transactions ("baseline"); after that
anything new triggers an alert. It is read-only: it can't move any money.
Free API limits are small, so keep the watch list short.
"""
import asyncio
from urllib.parse import quote
from discord.ext import commands
from main import infected
from cogs._store import load, save, get_json, post_webhook, valid_webhook, reply

CHAINS = {"btc": "bitcoin", "ltc": "litecoin", "doge": "dogecoin"}


class PayWatch(commands.Cog):
    """Incoming payment detector."""

    def __init__(self, bot):
        self.bot = bot
        self.task = None

    async def cog_unload(self):
        if self.task:
            self.task.cancel()

    async def _loop(self):
        try:
            while True:
                for w in list(load("watch", [])):
                    try:
                        c = CHAINS[w["chain"]]
                        d = await get_json(f"https://api.blockchair.com/{c}/dashboards/address/{quote(w['addr'])}",
                                           params={"limit": 5})
                        txs = list(d["data"].values())[0].get("transactions", [])
                        seen = load("watch_seen", {})
                        if w["addr"] not in seen:
                            seen[w["addr"]] = txs          # baseline
                        else:
                            new = [t for t in txs if t not in seen[w["addr"]]]
                            for t in new:
                                await post_webhook(load("watch_hook", ""),
                                                   f"**New {w['chain'].upper()} transaction** on `{w['addr'][:14]}...`\n"
                                                   f"https://blockchair.com/{c}/transaction/{t}")
                            if new:
                                seen[w["addr"]] = txs
                        save("watch_seen", seen)
                    except Exception:
                        pass
                    await asyncio.sleep(3)
                await asyncio.sleep(90)
        except asyncio.CancelledError:
            return

    @commands.command(name="setwatchhook", brief="Webhook for payment alerts", usage=".setwatchhook <webhook>")
    @infected()
    async def setwatchhook(self, ctx, url: str):
        if not valid_webhook(url):
            return await reply(ctx, "Pay watch", ["Not a valid webhook URL."], kind="error", delete_after=6)
        save("watch_hook", url)
        await reply(ctx, "Pay watch", ["Webhook saved."], kind="success", delete_after=6)

    @commands.command(name="watchaddy", brief="Watch an address", usage=".watchaddy <btc|ltc|doge> <address>")
    @infected()
    async def watchaddy(self, ctx, chain: str, address: str):
        if chain.lower() not in CHAINS:
            return await reply(ctx, "Pay watch", ["Chain must be btc, ltc or doge."], kind="error", delete_after=6)
        w = load("watch", [])
        if not any(x["addr"] == address for x in w):
            w.append({"chain": chain.lower(), "addr": address})
        save("watch", w)
        await reply(ctx, "Pay watch", [f"Watching {address[:16]}..."], kind="success", delete_after=8)

    @commands.command(name="unwatchaddy", brief="Stop watching an address", usage=".unwatchaddy <address>")
    @infected()
    async def unwatchaddy(self, ctx, address: str):
        save("watch", [x for x in load("watch", []) if x["addr"] != address])
        await reply(ctx, "Pay watch", ["Removed."], kind="success", delete_after=6)

    @commands.command(name="listwatch", brief="List watched addresses", usage=".listwatch")
    @infected()
    async def listwatch(self, ctx):
        await reply(ctx, "Pay watch", [f"{x['chain'].upper()} {x['addr']}" for x in load("watch", [])] or ["None."])

    @commands.command(name="startdetect", brief="Start payment detector", usage=".startdetect")
    @infected()
    async def startdetect(self, ctx):
        if not load("watch_hook", ""):
            return await reply(ctx, "Pay watch", ["Run .setwatchhook first."], kind="error", delete_after=6)
        if self.task:
            self.task.cancel()
        self.task = asyncio.create_task(self._loop())
        await reply(ctx, "Pay watch", ["Detector started."], kind="success", delete_after=6)

    @commands.command(name="stopdetect", brief="Stop payment detector", usage=".stopdetect")
    @infected()
    async def stopdetect(self, ctx):
        if self.task:
            self.task.cancel()
            self.task = None
        await reply(ctx, "Pay watch", ["Detector stopped."], kind="success", delete_after=6)


async def setup(bot):
    await bot.add_cog(PayWatch(bot))

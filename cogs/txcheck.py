"""
txcheck.py  -  look up a crypto transaction (read-only).

LEARN: we call a free public blockchain API (blockchair) with aiohttp, read the
JSON, and show a few fields. Nothing is sent or signed - it only READS the chain.
Confirmations = (latest block - tx block + 1).
"""
from urllib.parse import quote
from discord.ext import commands
from main import infected
from cogs._store import get_json, reply

CHAINS = {"btc": "bitcoin", "ltc": "litecoin", "doge": "dogecoin"}


class TxCheck(commands.Cog):
    """Transaction lookups."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="txid", brief="Check a BTC/LTC/DOGE transaction", usage=".txid <btc|ltc|doge> <txid>")
    @infected()
    async def txid(self, ctx, chain: str, txid: str):
        c = CHAINS.get(chain.lower())
        if not c:
            return await reply(ctx, "TXID", ["Chain must be btc, ltc or doge."], kind="error", delete_after=6)
        try:
            d = await get_json(f"https://api.blockchair.com/{c}/dashboards/transaction/{quote(txid)}")
            t = list(d["data"].values())[0]["transaction"]
            tip = d["context"]["state"]
            bid = t.get("block_id") or -1
            conf = (tip - bid + 1) if bid and bid > 0 else 0
            await reply(ctx, f"{chain.upper()} transaction", [
                f"Confirmations: {conf} {'(confirmed)' if conf >= 1 else '(pending)'}",
                f"Amount out   : {t['output_total'] / 1e8:.8f}",
                f"Fee          : {t['fee'] / 1e8:.8f}",
                f"Time         : {t['time']}",
            ], kind="success" if conf >= 1 else "info", command="crypto")
        except Exception:
            await reply(ctx, "TXID", ["Couldn't find that transaction."], kind="error", delete_after=8)

    @commands.command(name="trontx", brief="Check a TRON transaction", usage=".trontx <hash>")
    @infected()
    async def trontx(self, ctx, txhash: str):
        try:
            d = await get_json("https://apilist.tronscanapi.com/api/transaction-info", params={"hash": txhash})
            if not d or not d.get("hash"):
                return await reply(ctx, "TRON", ["Not found."], kind="error", delete_after=8)
            await reply(ctx, "TRON transaction", [
                f"Confirmed: {d.get('confirmed')}",
                f"Result   : {d.get('contractRet')}",
                f"From     : {d.get('ownerAddress')}",
                f"To       : {d.get('toAddress')}",
            ], command="crypto")
        except Exception:
            await reply(ctx, "TRON", ["Couldn't check that transaction."], kind="error", delete_after=8)


async def setup(bot):
    await bot.add_cog(TxCheck(bot))

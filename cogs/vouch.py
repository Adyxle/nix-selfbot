"""
vouch.py  -  ready-to-copy vouch lines for your store.

LEARN: f-strings build text; <@ID> is how Discord writes a mention.
ctx.author.id is YOU (the command author), so the line mentions you.
"""
from discord.ext import commands
from main import infected
from cogs._store import plain

STORE = "NixWil Market"


class Vouch(commands.Cog):
    """Vouch line generators."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="vouch", brief="Vouch line for a sale", usage=".vouch <product for price>")
    @infected()
    async def vouch(self, ctx, *, text: str):
        await plain(ctx, f"+rep <@{ctx.author.id}> Legit seller | {text} | {STORE}")

    @commands.command(name="n2cvouch", brief="Vouch: NPR to crypto", usage=".n2cvouch <npr> <crypto>")
    @infected()
    async def n2cvouch(self, ctx, npr: str, crypto: str):
        await plain(ctx, f"+rep <@{ctx.author.id}> Legit exchanger | NPR -> Crypto | Rs {npr} -> {crypto} | {STORE}")

    @commands.command(name="c2nvouch", brief="Vouch: crypto to NPR", usage=".c2nvouch <crypto> <npr>")
    @infected()
    async def c2nvouch(self, ctx, crypto: str, npr: str):
        await plain(ctx, f"+rep <@{ctx.author.id}> Legit exchanger | Crypto -> NPR | {crypto} -> Rs {npr} | {STORE}")


async def setup(bot):
    await bot.add_cog(Vouch(bot))

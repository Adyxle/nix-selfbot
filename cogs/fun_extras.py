"""
fun_extras.py  -  harmless fun commands (your fun.py is spam tools, so these live separately).

LEARN: `random.choice(list)` picks one item. Image commands just send the raw link so
Discord expands the picture itself - no embed needed.
"""
import random
from discord.ext import commands
from main import infected
from cogs._store import get_json, reply, plain

RIZZ = [
    "Are you a campfire? Because you're hot and I want s'more.",
    "Do you have a map? I keep getting lost in your eyes.",
    "Is your name Wi-Fi? Because I'm feeling a connection.",
    "Are you a keyboard? Because you're just my type.",
    "Do you believe in love at first text, or should I message again?",
]
BALL = ["Yes.", "No.", "Maybe.", "Definitely.", "Ask again later.", "Not a chance.", "Without a doubt.", "Very doubtful."]


class FunExtras(commands.Cog):
    """Memes, animals and small games."""

    def __init__(self, bot):
        self.bot = bot

    async def _link(self, ctx, url, pick):
        try:
            d = await get_json(url)
            await plain(ctx, pick(d))
        except Exception:
            await reply(ctx, "Fun", ["Couldn't fetch that right now."], kind="error", delete_after=6)

    @commands.command(name="meme", brief="Random meme", usage=".meme")
    @infected()
    async def meme(self, ctx):
        await self._link(ctx, "https://meme-api.com/gimme", lambda d: d["url"])

    @commands.command(name="cat", brief="Random cat", usage=".cat")
    @infected()
    async def cat(self, ctx):
        await self._link(ctx, "https://api.thecatapi.com/v1/images/search", lambda d: d[0]["url"])

    @commands.command(name="dog", brief="Random dog", usage=".dog")
    @infected()
    async def dog(self, ctx):
        await self._link(ctx, "https://dog.ceo/api/breeds/image/random", lambda d: d["message"])

    @commands.command(name="fox", brief="Random fox", usage=".fox")
    @infected()
    async def fox(self, ctx):
        await self._link(ctx, "https://randomfox.ca/floof/", lambda d: d["image"])

    @commands.command(name="joke", brief="Random joke", usage=".joke")
    @infected()
    async def joke(self, ctx):
        try:
            d = await get_json("https://official-joke-api.appspot.com/random_joke")
            await reply(ctx, "Joke", [d["setup"], d["punchline"]], delete_after=40)
        except Exception:
            await reply(ctx, "Joke", ["No joke right now."], kind="error", delete_after=6)

    @commands.command(name="rizz", brief="Random pickup line", usage=".rizz")
    @infected()
    async def rizz(self, ctx):
        await reply(ctx, "Rizz", [random.choice(RIZZ)], delete_after=40)

    @commands.command(name="8ball", brief="Magic 8-ball", usage=".8ball <question>")
    @infected()
    async def eightball(self, ctx, *, question: str):
        await reply(ctx, "8ball", [question, f"-> {random.choice(BALL)}"], delete_after=40)

    @commands.command(name="coinflip", brief="Flip a coin", usage=".coinflip")
    @infected()
    async def coinflip(self, ctx):
        await reply(ctx, "Coin", [random.choice(["Heads", "Tails"])], delete_after=20)

    @commands.command(name="roll", brief="Roll a die", usage=".roll [sides]")
    @infected()
    async def roll(self, ctx, sides: int = 6):
        await reply(ctx, "Dice", [str(random.randint(1, max(2, min(sides, 1000))))], delete_after=20)


async def setup(bot):
    await bot.add_cog(FunExtras(bot))

"""
tools.py  -  small handy tools: qr, translate, weather, mcip, checkurl, banner, icon, emojitoimg.

LEARN: most commands here are the same 3 steps -
  1) read the user's input   2) call a free API with get_json/get_text   3) reply.
`try/except` makes sure a failed web request shows a friendly error, not a crash.
"""
from urllib.parse import quote
import aiohttp
import discord
from discord.ext import commands
from main import infected
from cogs._store import get_json, get_text, reply, plain, HEADERS, TIMEOUT


class Tools(commands.Cog):
    """Handy extra tools."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="qr", brief="Make a QR code link", usage=".qr <text>")
    @infected()
    async def qr(self, ctx, *, text: str):
        # Raw link -> Discord shows the image by itself.
        await plain(ctx, f"https://api.qrserver.com/v1/create-qr-code/?size=400x400&data={quote(text)}")

    @commands.command(name="translate", aliases=["tr"], brief="Translate text", usage=".translate <from> <to> <text>")
    @infected()
    async def translate(self, ctx, src: str, dst: str, *, text: str):
        try:
            d = await get_json("https://api.mymemory.translated.net/get", params={"q": text, "langpair": f"{src}|{dst}"})
            await reply(ctx, f"{src} -> {dst}", [d["responseData"]["translatedText"]])
        except Exception:
            await reply(ctx, "Translate", ["Translation failed."], kind="error", delete_after=6)

    @commands.command(name="weather", brief="Weather for a city", usage=".weather <city>")
    @infected()
    async def weather(self, ctx, *, city: str):
        try:
            t = await get_text(f"https://wttr.in/{quote(city)}", params={"format": "3"})
            await reply(ctx, "Weather", [t.strip()])
        except Exception:
            await reply(ctx, "Weather", ["Couldn't get weather."], kind="error", delete_after=6)

    @commands.command(name="mcip", brief="Minecraft server status", usage=".mcip <server.ip>")
    @infected()
    async def mcip(self, ctx, ip: str):
        try:
            d = await get_json(f"https://api.mcsrvstat.us/3/{ip}")
            if not d.get("online"):
                return await reply(ctx, "Minecraft", [f"{ip} is offline."], kind="error", delete_after=10)
            p = d.get("players", {})
            await reply(ctx, "Minecraft", [f"{ip} is online", f"Players: {p.get('online', 0)}/{p.get('max', 0)}",
                                           f"Version: {d.get('version', '?')}"], kind="success")
        except Exception:
            await reply(ctx, "Minecraft", ["Couldn't check that server."], kind="error", delete_after=6)

    @commands.command(name="checkurl", brief="Follow redirects of a link", usage=".checkurl <url>")
    @infected()
    async def checkurl(self, ctx, url: str):
        try:
            async with aiohttp.ClientSession(headers=HEADERS, timeout=TIMEOUT) as s:
                async with s.get(url, allow_redirects=True) as r:
                    await reply(ctx, "URL check", [f"Status: {r.status}", f"Hops  : {len(r.history)}", f"Final : {r.url}"])
        except Exception:
            await reply(ctx, "URL check", ["Couldn't reach that URL."], kind="error", delete_after=6)

    @commands.command(name="banner", brief="Banner link of a user", usage=".banner [user]")
    @infected()
    async def banner(self, ctx, user: discord.User = None):
        user = user or ctx.author
        try:
            u = await self.bot.fetch_user(user.id)
            if u.banner:
                return await plain(ctx, u.banner.url)
            await reply(ctx, "Banner", ["No banner."], kind="error", delete_after=6)
        except Exception:
            await reply(ctx, "Banner", ["Couldn't fetch banner."], kind="error", delete_after=6)

    @commands.command(name="icon", brief="Server icon link", usage=".icon")
    @infected()
    async def icon(self, ctx):
        g = ctx.guild
        if g and g.icon:
            return await plain(ctx, g.icon.url)
        await reply(ctx, "Icon", ["No server icon."], kind="error", delete_after=6)

    @commands.command(name="emojitoimg", brief="Custom emoji as image link", usage=".emojitoimg <emoji>")
    @infected()
    async def emojitoimg(self, ctx, emoji: str):
        pe = discord.PartialEmoji.from_str(emoji)
        if pe.id:
            return await plain(ctx, str(pe.url))
        await reply(ctx, "Emoji", ["Use a custom emoji."], kind="error", delete_after=6)


async def setup(bot):
    await bot.add_cog(Tools(bot))

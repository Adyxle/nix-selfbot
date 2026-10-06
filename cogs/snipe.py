"""
snipe.py  -  see the last deleted / edited message in a channel.

LEARN: `@commands.Cog.listener()` makes a function run on a Discord EVENT
(on_message_delete, on_message_edit). We keep the last one per channel in a dict
in memory, so it resets when the bot restarts.
"""
from discord.ext import commands
from main import infected
from cogs._store import reply


class Snipe(commands.Cog):
    """Shows the last deleted/edited message per channel."""

    def __init__(self, bot):
        self.bot = bot
        self.deleted = {}   # channel_id -> (author, text)
        self.edited = {}

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.content:
            self.deleted[message.channel.id] = (str(message.author), message.content)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.content and before.content != after.content:
            self.edited[before.channel.id] = (str(before.author), before.content)

    @commands.command(name="snipe", brief="Last deleted message here", usage=".snipe")
    @infected()
    async def snipe(self, ctx):
        s = self.deleted.get(ctx.channel.id)
        if not s:
            return await reply(ctx, "Snipe", ["Nothing to snipe."], kind="error", delete_after=6, command="snipe")
        await reply(ctx, "Snipe", [f"Author : {s[0]}", f"Message: {s[1]}"], command="snipe")

    @commands.command(name="editsnipe", brief="Last edited message here", usage=".editsnipe")
    @infected()
    async def editsnipe(self, ctx):
        s = self.edited.get(ctx.channel.id)
        if not s:
            return await reply(ctx, "Edit snipe", ["Nothing to snipe."], kind="error", delete_after=6, command="snipe")
        await reply(ctx, "Edit snipe", [f"Author : {s[0]}", f"Before : {s[1]}"], command="snipe")


async def setup(bot):
    await bot.add_cog(Snipe(bot))

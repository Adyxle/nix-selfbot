import discord
from discord.ext import commands


class Purge(commands.Cog):
    """Deletes your own previous messages in a channel."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Deletes your own last N messages in this channel.")
    async def purge(self, ctx, amount: int = 10):
        """
        Deletes your own last N messages in this channel.
        Usage: ,purge 15   (defaults to 10 if no number given)
        """
        if amount < 1 or amount > 100:
            await ctx.send("Please choose a number between 1 and 100.")
            return

        deleted = 0
        async for msg in ctx.channel.history(limit=200):
            if msg.author.id == ctx.author.id:
                try:
                    await msg.delete()
                    deleted += 1
                except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                    pass
                if deleted >= amount:
                    break

        await ctx.send(f"Deleted {deleted} of your messages.")


async def setup(bot):
    await bot.add_cog(Purge(bot))

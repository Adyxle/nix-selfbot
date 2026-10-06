"""
vc_extra.py  -  more voice commands (your vc.py already has vc247, vckick, vcmoveall, vcmute).

LEARN: discord.VoiceChannel in a command signature makes discord.py convert an ID
or name into the real channel object for you (a "converter").
change_voice_state joins voice without needing audio libraries.
"""
import discord
from discord.ext import commands
from main import infected
from cogs._store import reply


async def done(ctx, text, ok=True):
    await reply(ctx, "Voice", [text], kind="success" if ok else "error", delete_after=8)


class VCExtra(commands.Cog):
    """More voice channel controls."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="vcjoin", brief="Join a voice channel (muted)", usage=".vcjoin <voice.channel>")
    @infected()
    async def vcjoin(self, ctx, channel: discord.VoiceChannel):
        try:
            await channel.guild.change_voice_state(channel=channel, self_mute=True, self_deaf=True)
            await done(ctx, f"Joined {channel.name}")
        except Exception as e:
            await done(ctx, f"Failed: {type(e).__name__}", ok=False)

    @commands.command(name="vcleave", brief="Leave voice", usage=".vcleave [voice.channel]")
    @infected()
    async def vcleave(self, ctx, channel: discord.VoiceChannel = None):
        guild = channel.guild if channel else ctx.guild
        if not guild:
            return await done(ctx, "Use in a server or give a channel.", ok=False)
        try:
            await guild.change_voice_state(channel=None)
            await done(ctx, "Left voice.")
        except Exception as e:
            await done(ctx, f"Failed: {type(e).__name__}", ok=False)

    async def _edit(self, ctx, member, **kw):
        try:
            await member.edit(**kw)
            await done(ctx, f"Done for {member}")
        except Exception as e:
            await done(ctx, f"Failed: {type(e).__name__}", ok=False)

    @commands.command(name="vcunmute", brief="Unmute a user", usage=".vcunmute <user>")
    @infected()
    async def vcunmute(self, ctx, user: discord.Member):
        await self._edit(ctx, user, mute=False)

    @commands.command(name="vcdeafen", brief="Deafen a user", usage=".vcdeafen <user>")
    @infected()
    async def vcdeafen(self, ctx, user: discord.Member):
        await self._edit(ctx, user, deafen=True)

    @commands.command(name="vcundeafen", brief="Undeafen a user", usage=".vcundeafen <user>")
    @infected()
    async def vcundeafen(self, ctx, user: discord.Member):
        await self._edit(ctx, user, deafen=False)

    @commands.command(name="vcmove", brief="Move a user to a voice channel", usage=".vcmove <user> <voice.channel>")
    @infected()
    async def vcmove(self, ctx, user: discord.Member, channel: discord.VoiceChannel):
        try:
            await user.move_to(channel)
            await done(ctx, f"Moved {user} to {channel.name}")
        except Exception as e:
            await done(ctx, f"Failed: {type(e).__name__}", ok=False)

    @commands.command(name="vclimit", brief="Set voice user limit (0 = none)", usage=".vclimit <limit> <voice.channel>")
    @infected()
    async def vclimit(self, ctx, limit: int, channel: discord.VoiceChannel):
        try:
            await channel.edit(user_limit=max(0, min(limit, 99)))
            await done(ctx, f"Limit set to {limit}")
        except Exception as e:
            await done(ctx, f"Failed: {type(e).__name__}", ok=False)


async def setup(bot):
    await bot.add_cog(VCExtra(bot))

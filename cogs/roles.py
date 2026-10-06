"""
roles.py  -  small server-management commands for servers you run
(your admin.py already has kick, ban, unban, softban, mute).

LEARN: Discord only lets you do these if your account has the permission, so each
command first checks `guild.me.guild_permissions`. If you don't have it, we say so
instead of crashing. `discord.Object(id=...)` lets you act on someone who isn't in
the server (like banning by ID).
"""
import discord
from discord.ext import commands
from main import infected
from cogs._store import reply


def missing(ctx, perm):
    """Return an error text if we can't do this here, else None."""
    if ctx.guild is None:
        return "Use this in a server."
    if not getattr(ctx.guild.me.guild_permissions, perm):
        return f"You need {perm} here."
    return None


async def fail(ctx, text):
    await reply(ctx, "Roles", [text], kind="error", delete_after=8)


async def ok(ctx, text):
    await reply(ctx, "Roles", [text], kind="success", delete_after=8)


class Roles(commands.Cog):
    """Roles, channel visibility and ban-by-ID."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="banid", brief="Ban by user ID", usage=".banid <user.id>")
    @infected()
    async def banid(self, ctx, user_id: int):
        err = missing(ctx, "ban_members")
        if err:
            return await fail(ctx, err)
        try:
            await ctx.guild.ban(discord.Object(id=user_id))
            await ok(ctx, f"Banned {user_id}")
        except Exception as e:
            await fail(ctx, f"Failed: {type(e).__name__}")

    @commands.command(name="hide", brief="Hide this channel from @everyone", usage=".hide")
    @infected()
    async def hide(self, ctx):
        err = missing(ctx, "manage_channels")
        if err:
            return await fail(ctx, err)
        await ctx.channel.set_permissions(ctx.guild.default_role, view_channel=False)
        await ok(ctx, "Channel hidden.")

    @commands.command(name="unhide", brief="Unhide this channel", usage=".unhide")
    @infected()
    async def unhide(self, ctx):
        err = missing(ctx, "manage_channels")
        if err:
            return await fail(ctx, err)
        await ctx.channel.set_permissions(ctx.guild.default_role, view_channel=None)
        await ok(ctx, "Channel visible again.")

    @commands.command(name="createrole", brief="Create a role", usage=".createrole <name>")
    @infected()
    async def createrole(self, ctx, *, name: str):
        err = missing(ctx, "manage_roles")
        if err:
            return await fail(ctx, err)
        await ctx.guild.create_role(name=name)
        await ok(ctx, f"Role '{name}' created.")

    @commands.command(name="role", brief="Toggle a role on a member", usage=".role <member> <role>")
    @infected()
    async def role(self, ctx, member: discord.Member, role: discord.Role):
        err = missing(ctx, "manage_roles")
        if err:
            return await fail(ctx, err)
        try:
            if role in member.roles:
                await member.remove_roles(role)
                await ok(ctx, f"Removed {role.name} from {member}")
            else:
                await member.add_roles(role)
                await ok(ctx, f"Gave {role.name} to {member}")
        except Exception as e:
            await fail(ctx, f"Failed: {type(e).__name__}")

    @commands.command(name="roleperms", brief="Show a role's permissions", usage=".roleperms <role>")
    @infected()
    async def roleperms(self, ctx, role: discord.Role):
        perms = [n.replace("_", " ") for n, v in role.permissions if v]
        await reply(ctx, f"{role.name} ({len(perms)})", [", ".join(perms) or "none"], delete_after=40)


async def setup(bot):
    await bot.add_cog(Roles(bot))

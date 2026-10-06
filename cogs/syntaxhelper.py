"""
syntaxhelper.py  -  when you type a command wrong, show the correct syntax.

WHAT CHANGED (v2): it now catches every kind of argument error, tells you WHICH
argument is missing/wrong, always shows the usage line from the command's `usage=`
(falling back to discord.py's auto signature), stays on screen for 20 seconds, and
prints a short line in your console so you can see it working.

LEARN: discord.py raises an *exception* when a command can't run. Cog listeners named
`on_command_error` receive it. We check what TYPE of exception it is and answer.
"""
import discord
from discord.ext import commands
from cogs._style import box

SHOW_FOR = 20  # seconds the message stays


class SyntaxHelper(commands.Cog):
    """Shows correct syntax when a command is used wrongly."""

    def __init__(self, bot):
        self.bot = bot

    def _usage(self, ctx):
        cmd = ctx.command
        if cmd.usage:
            return cmd.usage
        return f"{ctx.prefix or ''}{cmd.qualified_name} {cmd.signature}".strip()

    def _info(self, ctx):
        cmd = ctx.command
        return cmd.brief or cmd.description or (cmd.help or "").split("\n")[0] or "No description."

    async def _say(self, ctx, title, lines, kind="error"):
        name = ctx.command.qualified_name if ctx.command else None
        text = box(title, lines, kind=kind, command=name)
        try:
            await ctx.send(text, delete_after=SHOW_FOR)
        except Exception:
            try:
                await ctx.channel.send(text, delete_after=SHOW_FOR)
            except Exception as e:
                print(f"[syntaxhelper] could not send message: {e!r}")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound) or ctx.command is None:
            return  # typo of a command that doesn't exist - stay quiet

        error = getattr(error, "original", error)  # unwrap CommandInvokeError
        print(f"[syntaxhelper] {ctx.command.qualified_name}: {type(error).__name__}: {error}")

        # ---- wrong / missing arguments ----
        if isinstance(error, commands.MissingRequiredArgument):
            return await self._say(ctx, "Missing argument", [
                f"You forgot: {error.param.name}",
                f"Syntax : {self._usage(ctx)}",
                f"Info   : {self._info(ctx)}",
            ])

        if isinstance(error, commands.TooManyArguments):
            return await self._say(ctx, "Too many arguments", [
                f"Syntax : {self._usage(ctx)}",
                f"Info   : {self._info(ctx)}",
            ])

        if isinstance(error, (commands.BadArgument, commands.BadUnionArgument,
                              commands.ArgumentParsingError, commands.UserInputError)):
            return await self._say(ctx, "Invalid argument", [
                f"Problem: {error}",
                f"Syntax : {self._usage(ctx)}",
                f"Info   : {self._info(ctx)}",
            ])

        # ---- checks / context ----
        if isinstance(error, commands.NoPrivateMessage):
            return await self._say(ctx, "Server only", ["That command can't be used in DMs."])
        if isinstance(error, commands.PrivateMessageOnly):
            return await self._say(ctx, "DM only", ["That command only works in DMs."])
        if isinstance(error, commands.MissingPermissions):
            return await self._say(ctx, "No permission", [
                "You need: " + ", ".join(p.replace("_", " ") for p in error.missing_permissions)])
        if isinstance(error, commands.CheckFailure):
            return await self._say(ctx, "Blocked", ["You can't use that command here."])
        if isinstance(error, commands.CommandOnCooldown):
            return await self._say(ctx, "Cooldown", [f"Try again in {error.retry_after:.1f}s."], kind="warning")
        if isinstance(error, commands.DisabledCommand):
            return await self._say(ctx, "Disabled", ["That command is disabled."], kind="warning")

        # ---- Discord refused something ----
        if isinstance(error, discord.Forbidden):
            return await self._say(ctx, "Forbidden", ["Discord says you don't have permission for that."])
        if isinstance(error, discord.HTTPException):
            return await self._say(ctx, "Discord error", [f"{error.status}: {str(error.text)[:150]}"])

        # ---- anything else: show a short error and print the details in the console ----
        print(f"[syntaxhelper] unhandled error in {ctx.command}: {error!r}")
        await self._say(ctx, "Something went wrong", [str(error)[:300] or type(error).__name__])


async def setup(bot):
    await bot.add_cog(SyntaxHelper(bot))
    print("[syntaxhelper] loaded")

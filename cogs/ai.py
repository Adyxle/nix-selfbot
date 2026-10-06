"""
ai.py  -  .ai <message> : chat with Claude from Discord.

SETUP: in your .env file add  ANTHROPIC_API_KEY=your_key   (python-decouple reads it,
the same way main.py reads your token). Optional: ANTHROPIC_MODEL=...

LEARN: we keep the last few messages per channel in memory so the AI remembers the
conversation (`.resetai` clears it). The request is a normal HTTPS POST with JSON.
"""
from decouple import config
from discord.ext import commands
from main import infected
from cogs._store import load, save, get_json, reply

API_KEY = config("ANTHROPIC_API_KEY", default="")
MODEL = config("ANTHROPIC_MODEL", default="claude-sonnet-5-5")
DEFAULT_PROMPT = "You are a helpful assistant. Keep replies under 1500 characters."


class AI(commands.Cog):
    """AI chat."""

    def __init__(self, bot):
        self.bot = bot
        self.history = {}  # channel_id -> list of messages

    @commands.command(name="ai", brief="Talk with AI", usage=".ai <message>")
    @infected()
    async def ai(self, ctx, *, msg: str):
        if not API_KEY:
            return await reply(ctx, "AI", ["Add ANTHROPIC_API_KEY to your .env first."], kind="error", delete_after=8)
        hist = self.history.setdefault(ctx.channel.id, [])
        hist.append({"role": "user", "content": msg})
        hist[:] = hist[-10:]
        try:
            d = await get_json(
                "https://api.anthropic.com/v1/messages", method="POST",
                headers={"x-api-key": API_KEY, "anthropic-version": "2023-06-01"},
                body={"model": MODEL, "max_tokens": 700,
                      "system": load("ai_prompt", "") or DEFAULT_PROMPT, "messages": hist},
            )
            answer = "".join(b.get("text", "") for b in d.get("content", []))
            hist.append({"role": "assistant", "content": answer})
            await reply(ctx, "AI", [f"You: {msg[:200]}", "", answer], delete_after=90)
        except Exception:
            hist.pop()
            await reply(ctx, "AI", ["Request failed."], kind="error", delete_after=8)

    @commands.command(name="resetai", brief="Clear AI memory here", usage=".resetai")
    @infected()
    async def resetai(self, ctx):
        self.history.pop(ctx.channel.id, None)
        await reply(ctx, "AI", ["Memory cleared."], kind="success", delete_after=6)

    @commands.command(name="setprompt", brief="Set AI system prompt", usage=".setprompt <prompt>")
    @infected()
    async def setprompt(self, ctx, *, prompt: str):
        save("ai_prompt", prompt)
        await reply(ctx, "AI", ["Prompt saved."], kind="success", delete_after=6)

    @commands.command(name="resetprompt", brief="Reset AI prompt", usage=".resetprompt")
    @infected()
    async def resetprompt(self, ctx):
        save("ai_prompt", "")
        await reply(ctx, "AI", ["Prompt reset."], kind="success", delete_after=6)

    @commands.command(name="showprompt", brief="Show AI prompt", usage=".showprompt")
    @infected()
    async def showprompt(self, ctx):
        await reply(ctx, "AI prompt", [load("ai_prompt", "") or DEFAULT_PROMPT], delete_after=40)


async def setup(bot):
    await bot.add_cog(AI(bot))

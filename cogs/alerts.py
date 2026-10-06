"""
alerts.py  -  get pinged privately (via YOUR webhook) when something happens.

LEARN:
 * A webhook is a URL that lets you post into one channel. Make one in a private
   channel: Channel settings -> Integrations -> Webhooks.
 * `on_message` is an event listener - it runs for EVERY message the bot sees.
 * Settings are saved in alerts.json so they survive restarts.
 * Run the set...hook commands in a private place - the URL is a secret.
"""
import discord
import re
from discord.ext import commands
from main import infected
from cogs._store import load, save, reply, post_webhook, valid_webhook


def cfg():
    return load("alerts", {})


def put(key, value):
    d = cfg()
    d[key] = value
    save("alerts", d)


def where(m):
    return "DM" if m.guild is None else f"{m.guild.name} #{getattr(m.channel, 'name', '?')}"


class Alerts(commands.Cog):
    """Mention, keyword, role-ping and DM-log alerts + DM greeter."""

    def __init__(self, bot):
        self.bot = bot

    # ---------------- events ----------------
    @commands.Cog.listener()
    async def on_message(self, m):
        me = self.bot.user
        if m.author.id == me.id:
            return
        c = cfg()
        text = (m.content or "")[:600]
        link = getattr(m, "jump_url", "")

        if c.get("mention_on") and any(u.id == me.id for u in m.mentions):
            await post_webhook(c.get("mention_hook"), f"**Mention** | {where(m)} | {m.author}\n{text}\n{link}")

        if c.get("kw_on"):
            low = text.lower()
            for k in c.get("keywords", []):
                if re.search(rf"\b{re.escape(k)}\b", low):
                    await post_webhook(c.get("kw_hook"), f"**Keyword `{k}`** | {where(m)} | {m.author}\n{text}\n{link}")
                    break

        if c.get("role_on") and m.role_mentions:
            watch = c.get("roles", [])
            for r in m.role_mentions:
                if str(r.id) in watch or r.name.lower() in watch:
                    await post_webhook(c.get("role_hook"), f"**Role ping `{r.name}`** | {where(m)} | {m.author}\n{text}\n{link}")
                    break

        # DM greeter: greet people who DM you first - once each
        if isinstance(m.channel, discord.DMChannel) and c.get("greet_on") and c.get("greet_text"):
            greeted = c.get("greeted", [])
            if m.author.id in greeted:
                return
            try:
                async for old in m.channel.history(limit=20):
                    if old.author.id == me.id:
                        return  # you've talked before, don't greet
                await m.channel.send(c["greet_text"])
                greeted.append(m.author.id)
                put("greeted", greeted)
            except Exception as e:
                print(f"[alerts] greeter failed for {m.author.id}: {e}")

    @commands.Cog.listener()
    async def on_message_delete(self, m):
        c = cfg()
        if c.get("log_on") and m.author.id != self.bot.user.id and isinstance(m.channel, (discord.DMChannel, discord.GroupChannel)):
            await post_webhook(c.get("log_hook"), f"**Deleted** | {m.author}\n{m.content[:1500]}")

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        c = cfg()
        if c.get("log_on") and before.author.id != self.bot.user.id and before.content != after.content \
                and isinstance(before.channel, (discord.DMChannel, discord.GroupChannel)):
            await post_webhook(c.get("log_hook"), f"**Edited** | {before.author}\nBefore: {before.content[:700]}\nAfter: {after.content[:700]}")

    # ---------------- helpers for commands ----------------
    async def _hook(self, ctx, key, url, label):
        if not valid_webhook(url):
            return await reply(ctx, label, ["Not a valid webhook URL."], kind="error", delete_after=6)
        put(key, url)
        await reply(ctx, label, ["Webhook saved."], kind="success", delete_after=6)

    async def _switch(self, ctx, on_key, hook_key, value, label):
        if value and not cfg().get(hook_key):
            return await reply(ctx, label, ["Set the webhook first."], kind="error", delete_after=6)
        put(on_key, value)
        await reply(ctx, label, ["ON" if value else "OFF"], kind="success", delete_after=6)

    # ---------------- DM log ----------------
    @commands.command(name="setloghook", brief="Webhook for DM log", usage=".setloghook <webhook>")
    @infected()
    async def setloghook(self, ctx, url: str):
        await self._hook(ctx, "log_hook", url, "DM log")

    @commands.command(name="logon", brief="Log deleted/edited DMs", usage=".logon")
    @infected()
    async def logon(self, ctx):
        await self._switch(ctx, "log_on", "log_hook", True, "DM log")

    @commands.command(name="logoff", brief="Stop DM log", usage=".logoff")
    @infected()
    async def logoff(self, ctx):
        await self._switch(ctx, "log_on", "log_hook", False, "DM log")

    # ---------------- mentions ----------------
    @commands.command(name="setmentionhook", brief="Webhook for mention alerts", usage=".setmentionhook <webhook>")
    @infected()
    async def setmentionhook(self, ctx, url: str):
        await self._hook(ctx, "mention_hook", url, "Mention alert")

    @commands.command(name="mentionon", brief="Mention alerts on", usage=".mentionon")
    @infected()
    async def mentionon(self, ctx):
        await self._switch(ctx, "mention_on", "mention_hook", True, "Mention alert")

    @commands.command(name="mentionoff", brief="Mention alerts off", usage=".mentionoff")
    @infected()
    async def mentionoff(self, ctx):
        await self._switch(ctx, "mention_on", "mention_hook", False, "Mention alert")

    # ---------------- keywords ----------------
    @commands.command(name="setkeywordhook", brief="Webhook for keyword alerts", usage=".setkeywordhook <webhook>")
    @infected()
    async def setkeywordhook(self, ctx, url: str):
        await self._hook(ctx, "kw_hook", url, "Keyword alert")

    @commands.command(name="addkeyword", brief="Add keyword", usage=".addkeyword <word>")
    @infected()
    async def addkeyword(self, ctx, *, word: str):
        kws = cfg().get("keywords", [])
        if word.lower() not in kws:
            kws.append(word.lower())
        put("keywords", kws)
        await reply(ctx, "Keywords", [f"Added: {word}"], kind="success", delete_after=6)

    @commands.command(name="removekeyword", brief="Remove keyword", usage=".removekeyword <word>")
    @infected()
    async def removekeyword(self, ctx, *, word: str):
        put("keywords", [k for k in cfg().get("keywords", []) if k != word.lower()])
        await reply(ctx, "Keywords", [f"Removed: {word}"], kind="success", delete_after=6)

    @commands.command(name="keywordlist", brief="List keywords", usage=".keywordlist")
    @infected()
    async def keywordlist(self, ctx):
        await reply(ctx, "Keywords", cfg().get("keywords", []) or ["None."])

    @commands.command(name="keywordon", brief="Keyword alerts on", usage=".keywordon")
    @infected()
    async def keywordon(self, ctx):
        await self._switch(ctx, "kw_on", "kw_hook", True, "Keyword alert")

    @commands.command(name="keywordoff", brief="Keyword alerts off", usage=".keywordoff")
    @infected()
    async def keywordoff(self, ctx):
        await self._switch(ctx, "kw_on", "kw_hook", False, "Keyword alert")

    # ---------------- role pings ----------------
    @commands.command(name="setrolehook", brief="Webhook for role-ping alerts", usage=".setrolehook <webhook>")
    @infected()
    async def setrolehook(self, ctx, url: str):
        await self._hook(ctx, "role_hook", url, "Role ping alert")

    @commands.command(name="addrole", brief="Watch a role ping", usage=".addrole <role name or id>")
    @infected()
    async def addrole(self, ctx, *, role: str):
        roles = cfg().get("roles", [])
        if role.lower() not in roles:
            roles.append(role.lower())
        put("roles", roles)
        await reply(ctx, "Role pings", [f"Watching: {role}"], kind="success", delete_after=6)

    @commands.command(name="removerole", brief="Stop watching a role", usage=".removerole <role name or id>")
    @infected()
    async def removerole(self, ctx, *, role: str):
        put("roles", [r for r in cfg().get("roles", []) if r != role.lower()])
        await reply(ctx, "Role pings", [f"Removed: {role}"], kind="success", delete_after=6)

    @commands.command(name="roleon", brief="Role-ping alerts on", usage=".roleon")
    @infected()
    async def roleon(self, ctx):
        await self._switch(ctx, "role_on", "role_hook", True, "Role ping alert")

    @commands.command(name="roleoff", brief="Role-ping alerts off", usage=".roleoff")
    @infected()
    async def roleoff(self, ctx):
        await self._switch(ctx, "role_on", "role_hook", False, "Role ping alert")

    # ---------------- greeter ----------------
    @commands.command(name="setgreet", brief="Set + enable DM greeting", usage=".setgreet <text>")
    @infected()
    async def setgreet(self, ctx, *, text: str):
        put("greet_text", text)
        put("greet_on", True)
        await reply(ctx, "Greeter", ["Saved and ON."], kind="success", delete_after=6)

    @commands.command(name="greetoff", brief="Turn greeter off", usage=".greetoff")
    @infected()
    async def greetoff(self, ctx):
        put("greet_on", False)
        await reply(ctx, "Greeter", ["OFF"], kind="success", delete_after=6)

    @commands.command(name="cleargreet", brief="Clear greeting + history", usage=".cleargreet")
    @infected()
    async def cleargreet(self, ctx):
        put("greet_text", "")
        put("greet_on", False)
        put("greeted", [])
        await reply(ctx, "Greeter", ["Cleared."], kind="success", delete_after=6)


async def setup(bot):
    await bot.add_cog(Alerts(bot))

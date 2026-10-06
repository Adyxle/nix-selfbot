import discord
from discord.ext import commands
from discord.ext import tasks
import json
import os
import time

CONFIG_PATH = "svm_config.json"
PRESETS_PATH = "svm_presets.json"
MIN_INTERVAL = 30


class SVM(commands.Cog):
    """Configurable auto-repeating messages with rotating presets, per channel."""

    def __init__(self, bot):
        self.bot = bot
        self.config = self._load_json(CONFIG_PATH)     # channel_id -> config
        self.presets = self._load_json(PRESETS_PATH)    # label -> message text
        self.active = {}  # channel_id -> bool
        self.sender_loop.start()

    def cog_unload(self):
        self.sender_loop.cancel()

    def _load_json(self, path):
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
        return {}

    def _save_json(self, path, data):
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def _save_config(self):
        self._save_json(CONFIG_PATH, self.config)

    def _save_presets(self):
        self._save_json(PRESETS_PATH, self.presets)

    # ---------- preset management ----------

    @commands.command(description="Save a prerecorded message under a label.")
    async def svmadd(self, ctx, label: str, *, message: str):
        """Save a prerecorded message under a label. Usage: ,svmadd greeting Hello everyone!"""
        self.presets[label.lower()] = message
        self._save_presets()
        await ctx.send(f"Saved preset '{label}'.")

    @commands.command(description="Bulk-add presets from an attached .txt file, one message per line.")
    async def svmbulkadd(self, ctx, prefix: str = "msg"):
        """
        Bulk-add presets from an attached .txt file (one message per line).
        Usage: attach a .txt file, then ,svmbulkadd [prefix]
        Presets are saved as prefix1, prefix2, prefix3...
        """
        if not ctx.message.attachments:
            await ctx.send("Attach a .txt file with one message per line.")
            return

        attachment = ctx.message.attachments[0]
        if not attachment.filename.endswith(".txt"):
            await ctx.send("File must be a .txt file.")
            return

        raw = await attachment.read()
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            await ctx.send("Couldn't decode the file as UTF-8 text.")
            return

        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if not lines:
            await ctx.send("File was empty.")
            return

        added = []
        for i, line in enumerate(lines, 1):
            label = f"{prefix}{i}"
            self.presets[label] = line
            added.append(label)

        self._save_presets()
        await ctx.send(f"Added {len(added)} presets: {added[0]} through {added[-1]}")

    @commands.command(description="Delete a saved preset.")
    async def svmdel(self, ctx, label: str):
        """Delete a saved preset."""
        label = label.lower()
        if label not in self.presets:
            await ctx.send("No preset with that label.")
            return
        del self.presets[label]
        self._save_presets()
        await ctx.send(f"Deleted preset '{label}'.")

    @commands.command(description="List saved presets, 20 per page.")
    async def svmpresets(self, ctx, page: int = 1):
        """List saved presets, paginated (20 per page). Usage: ,svmpresets [page]"""
        if not self.presets:
            await ctx.send("No presets saved yet. Use ,svmadd or ,svmbulkadd.")
            return

        items = list(self.presets.items())
        per_page = 20
        total_pages = (len(items) + per_page - 1) // per_page
        page = max(1, min(page, total_pages))

        start = (page - 1) * per_page
        chunk = items[start:start + per_page]

        lines = [f"{label} — \"{text[:40]}\"" for label, text in chunk]
        header = f"Page {page}/{total_pages} ({len(items)} total)\n\n"
        await ctx.send(header + "\n".join(lines))

    # ---------- channel configuration ----------

    @commands.command(description="Configure a channel with a single raw message.")
    async def svmset(self, ctx, server_id: int, channel_id: int, delay: int, *, message: str):
        """
        Configure a channel with a single raw message (not a saved preset).
        Usage: ,svmset <server_id> <channel_id> <delay> <message>
        """
        if delay < MIN_INTERVAL:
            await ctx.send(f"Delay must be at least {MIN_INTERVAL} seconds.")
            return

        guild = self.bot.get_guild(server_id)
        if guild is None:
            await ctx.send("I'm not in a server with that ID.")
            return
        channel = guild.get_channel(channel_id)
        if channel is None:
            await ctx.send("That channel ID wasn't found in that server.")
            return

        cid = str(channel_id)
        self.config[cid] = {
            "guild_id": server_id,
            "channel_id": channel_id,
            "messages": [message],
            "rotate_index": 0,
            "delay": delay,
            "last_sent": 0,
        }
        self._save_config()
        await ctx.send(f"Configured channel {channel_id} with a custom message. Run ,svm {channel_id} to start.")

    @commands.command(description="Configure a channel using one or more saved presets, rotating through them.")
    async def svmsetp(self, ctx, server_id: int, channel_id: int, delay: int, *labels: str):
        """
        Configure a channel using one or more saved presets (rotates through them each send).
        Usage: ,svmsetp <server_id> <channel_id> <delay> <label1> [label2] [label3] ...
        """
        if delay < MIN_INTERVAL:
            await ctx.send(f"Delay must be at least {MIN_INTERVAL} seconds.")
            return
        if not labels:
            await ctx.send("Provide at least one preset label.")
            return

        missing = [l for l in labels if l.lower() not in self.presets]
        if missing:
            await ctx.send(f"Unknown preset label(s): {', '.join(missing)}")
            return

        guild = self.bot.get_guild(server_id)
        if guild is None:
            await ctx.send("I'm not in a server with that ID.")
            return
        channel = guild.get_channel(channel_id)
        if channel is None:
            await ctx.send("That channel ID wasn't found in that server.")
            return

        messages = [self.presets[l.lower()] for l in labels]
        cid = str(channel_id)
        self.config[cid] = {
            "guild_id": server_id,
            "channel_id": channel_id,
            "messages": messages,
            "rotate_index": 0,
            "delay": delay,
            "last_sent": 0,
        }
        self._save_config()
        await ctx.send(
            f"Configured channel {channel_id} with {len(messages)} rotating preset(s). "
            f"Run ,svm {channel_id} to start."
        )

    @commands.command(description="Configure a channel using every preset that starts with a given prefix.")
    async def svmsetpfx(self, ctx, server_id: int, channel_id: int, delay: int, prefix: str):
        """
        Configure a channel to rotate through every preset starting with a prefix.
        Usage: ,svmsetpfx <server_id> <channel_id> <delay> <prefix>
        Example: ,svmsetpfx 123 456 60 msg   -> uses msg1, msg2, msg3...
        """
        if delay < MIN_INTERVAL:
            await ctx.send(f"Delay must be at least {MIN_INTERVAL} seconds.")
            return

        matching = [v for k, v in self.presets.items() if k.startswith(prefix.lower())]
        if not matching:
            await ctx.send(f"No presets found starting with '{prefix}'.")
            return

        guild = self.bot.get_guild(server_id)
        if guild is None:
            await ctx.send("I'm not in a server with that ID.")
            return
        channel = guild.get_channel(channel_id)
        if channel is None:
            await ctx.send("That channel ID wasn't found in that server.")
            return

        cid = str(channel_id)
        self.config[cid] = {
            "guild_id": server_id,
            "channel_id": channel_id,
            "messages": matching,
            "rotate_index": 0,
            "delay": delay,
            "last_sent": 0,
        }
        self._save_config()
        await ctx.send(f"Configured channel {channel_id} with {len(matching)} presets (prefix '{prefix}').")

    @commands.command(description="Change the delay for an existing channel config.")
    async def svmdelay(self, ctx, channel_id: int, delay: int):
        """Change the delay for an existing config without resetting the messages."""
        cid = str(channel_id)
        if cid not in self.config:
            await ctx.send("No config for that channel ID.")
            return
        if delay < MIN_INTERVAL:
            await ctx.send(f"Delay must be at least {MIN_INTERVAL} seconds.")
            return
        self.config[cid]["delay"] = delay
        self._save_config()
        await ctx.send(f"Delay updated to {delay}s for channel {channel_id}.")

    @commands.command(description="Start or stop the auto-message loop for a configured channel.")
    async def svm(self, ctx, channel_id: int):
        """Toggle the auto-message loop on/off for a configured channel."""
        cid = str(channel_id)
        if cid not in self.config:
            await ctx.send("No config for that channel ID. Use ,svmset, ,svmsetp, or ,svmsetpfx first.")
            return

        if self.active.get(cid):
            self.active[cid] = False
            await ctx.send(f"Stopped for channel {channel_id}.")
        else:
            self.active[cid] = True
            self.config[cid]["last_sent"] = 0
            self._save_config()
            delay = self.config[cid]["delay"]
            await ctx.send(f"Started for channel {channel_id}. Every {delay}s.")

    @commands.command(description="List every configured channel and its status.")
    async def svmlist(self, ctx):
        """List all configured channels and their status."""
        if not self.config:
            await ctx.send("No channels configured.")
            return
        lines = []
        for cid, entry in self.config.items():
            status = "running" if self.active.get(cid) else "stopped"
            count = len(entry.get("messages", []))
            lines.append(f"{cid} — {status} — every {entry['delay']}s — {count} message(s)")
        await ctx.send("\n".join(lines))

    @commands.command(description="Show full config and status for one channel.")
    async def svmstatus(self, ctx, channel_id: int):
        """Show full config for one channel."""
        cid = str(channel_id)
        entry = self.config.get(cid)
        if not entry:
            await ctx.send("No config for that channel ID.")
            return
        running = "running" if self.active.get(cid) else "stopped"
        msgs = "\n".join(f"  {i+1}. {m[:50]}" for i, m in enumerate(entry["messages"]))
        await ctx.send(
            f"Server ID: {entry['guild_id']}\nChannel ID: {entry['channel_id']}\n"
            f"Status: {running}\nDelay: {entry['delay']}s\nMessages:\n{msgs}"
        )

    # ---------- sender loop ----------

    @tasks.loop(seconds=5)
    async def sender_loop(self):
        now = time.time()

        for cid, is_active in list(self.active.items()):
            if not is_active:
                continue

            entry = self.config.get(cid)
            if not entry:
                continue

            delay = entry.get("delay", MIN_INTERVAL)
            last_sent = entry.get("last_sent", 0)
            if now - last_sent < delay:
                continue

            channel = self.bot.get_channel(int(cid))
            if channel is None:
                continue

            messages = entry.get("messages", [])
            if not messages:
                continue

            idx = entry.get("rotate_index", 0) % len(messages)
            text = messages[idx]

            try:
                await channel.send(text)
                entry["last_sent"] = now
                entry["rotate_index"] = (idx + 1) % len(messages)
                self._save_config()
            except (discord.Forbidden, discord.HTTPException):
                pass

    @sender_loop.before_loop
    async def before_sender_loop(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(SVM(bot))

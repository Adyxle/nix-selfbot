# Noir Self Utility

A Discord self-bot utility built on discord.py-self.

**Owner:** s0zv
**Community:** discord.gg/noirs

See `TERMS_OF_SERVICE.md` for the full terms, including the no-reselling policy and liability disclaimer. By using this project you agree to those terms.

## Setup

1. Install Python 3.12.
2. Create a `.env` file in the project root with the following values:
   ```
   token=your_discord_token_here
   prefix=,
   userid=your_discord_user_id_here
   DELETE_DELAY=4
   STARTUP_CHANNEL_ID=your_channel_id_here
   ```
3. Run the bot:
   ```
   python main.py
   ```
   `main.py` installs its own dependencies on startup (discord.py-self, python-decouple, colorama, Pillow), then loads every cog in the `cogs/` folder automatically.

## How it works

- `main.py` is the entry point. It builds the bot, logs in with your token, and loads every `.py` file in `cogs/` that doesn't start with an underscore.
- Files in `cogs/` starting with `_` (like `_style.py`, `_module_descriptions.py`) are shared helpers, not standalone modules, and are skipped by the loader on purpose.
- All command output is automatically boxed and styled by `autostyle.py` + `_style.py`, and auto-deletes after a short delay (configurable per-command).
- `,help` lists every loaded module and its command count. `,help <module>` shows that module's commands. `,help <command>` shows full syntax, aliases, and description.

## Support

Updates and bug fixes are provided through discord.gg/noirs for legitimate, non-resold copies only. See `TERMS_OF_SERVICE.md` Section 4 for what happens if that's violated.

## Disclaimer

This is a self-bot. Running it is against Discord's Terms of Service and carries real risk of account action (warnings, suspensions, bans) independent of anything in this codebase. See `TERMS_OF_SERVICE.md` Section 5 for the full risk acknowledgment — you are using this entirely at your own risk.

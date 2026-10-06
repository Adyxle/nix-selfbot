import os
import sys
os.system('pip uninstall discord.py -y')
os.system('pip install -r infreq.txt')
os.system('pip install -U discord.py-self')
os.system('pip uninstall decouple -y')
os.system('pip install python-decouple colorama')

import discord
import asyncio
from discord.ext import commands
from decouple import config
from colorama import Fore, Style

sys.modules.setdefault("main", sys.modules["__main__"])

infectpre = config('prefix')
bot = commands.Bot(command_prefix=infectpre, self_bot=True, help_command=None)

authorized_user = int(config("userid"))


@bot.event
async def on_message(message):
    if message.author != bot.user:
        return

    await bot.process_commands(message)


def infected():
    def predicate(ctx):
        return ctx.author.id == authorized_user
    return commands.check(predicate)


@bot.command()
@infected()
async def allcmds(ctx):
    command_list = bot.commands
    sorted_commands = sorted(command_list, key=lambda x: x.name)

    response = "# **NixWil Bot Cmds**\n\n"
    for command in sorted_commands:
        response += f"_{command.name}_, "

    await ctx.send(response, delete_after=30)


infection = config('token')


@bot.event
async def on_ready():
    nixwilbanner = """
NixWil Bot is connected.
"""

    print(Fore.RED + nixwilbanner + Style.RESET_ALL)
    print(f"{'='*30}")
    print(f"        Logged in as: {bot.user.name}")
    print(f"        Selfbot ID: {bot.user.id}")
    print(f"{'='*30}\n")
    print("NixWil Bot is connected")
    print(f"{'-'*30}")
    print(f"   Username: {bot.user.name}")
    print(f"   Guilds: {len(bot.guilds)}")
    print(f"   Members: {sum([guild.member_count or 0 for guild in bot.guilds])}")
    print(f"{'-'*30}")


async def load_cogs():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py') and not filename.startswith('_'):
            cog_name = filename[:-3]
            try:
                await bot.load_extension(f'cogs.{cog_name}')
                print(f"Loaded {filename}")
            except Exception as e:
                print(f"Failed {filename}: {e}")


@bot.event
async def setup_hook():
    await load_cogs()


bot.run(infection, reconnect=True)

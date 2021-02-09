#!/usr/bin/env python
import aiohttp
import discord
import json
import os
from discord.ext import commands

extensions = (
    "cogs.admin",
    "cogs.assbook",
)


def get_prefix(bot, message):
    """A callable Prefix for our bot. This could be edited to allow per server prefixes."""

    prefixes = ["!", "?", "ass "]

    # Check to see if we are outside of a guild. e.g DM's etc.
    # if not message.guild:
    # Only allow ? to be used in DMs
    #   return '?'

    # If we are in a guild, we allow for the user to mention us or use any of the prefixes in our list.
    return commands.when_mentioned_or(*prefixes)(bot, message)


class Assbot(commands.Bot):
    """
    A bot made for the website assbook
    """

    def __init__(self):
        super().__init__(
            command_prefix=get_prefix,
            case_insensitive=True,
            allowed_mentions=discord.AllowedMentions(
                everyone=False, users=True, roles=False
            ),
            help_command=commands.MinimalHelpCommand(),
        )
        if not os.path.exists("./config.json"):
            with open("./config.json", "w") as f:
                self.config = {}
                json.dump(self.config, f)
        else:
            with open("./config.json") as f:
                self.config = json.load(f)

        for extension in extensions:
            self.load_extension(extension)

    async def on_ready(self):
        self.session = aiohttp.ClientSession(
            raise_for_status=True, headers={"User-Agent": "AssbookDiscordBot"}
        )
        await self.change_presence(activity=discord.Game("with an ass on my book"))
        print("Ready!")

    async def on_command_error(self, ctx, error):
        print(error)
        await ctx.author.send(error)
        await ctx.reply("Something went wrong")

    async def close(self):
        try:
            await self.session.close()
        finally:
            await super().close()

    def run(self):
        super().run(self.config["token"], reconnect=True)


if __name__ == "__main__":
    bot = Assbot()
    bot.run()

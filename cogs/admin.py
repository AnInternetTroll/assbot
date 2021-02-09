import asyncio
import json
import os
import subprocess

import discord
import git
from discord.ext import commands


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def is_mod(ctx):
        return ctx.author.guild_permissions.manage_channels

    @commands.command(aliases=["quit"], hidden=True)
    @commands.check(is_mod)
    async def forceexit(self, ctx):
        await ctx.send("Self Destructing")
        await ctx.bot.close()

    @commands.command()
    @commands.check(is_mod)
    async def pull(self, ctx):
        """Update the bot from github"""
        g = git.cmd.Git(os.getcwd())
        try:
            await ctx.send(f"Probably pulled.\n```bash\n{g.pull()}```")
        except Exception as e:
            await ctx.send(f"An error has occured when pulling```bash\n{e}```")

    @commands.command(name="reload", hidden=True, usage="<extension>")
    @commands.check(is_mod)
    async def _reload(self, ctx, ext):
        """Reloads an extension"""
        try:
            self.bot.reload_extension(f"cogs.{ext}")
            await ctx.send(f"The extension {ext} was reloaded!")
        except commands.ExtensionNotFound:
            await ctx.send(f"The extension {ext} doesn't exist.")
        except commands.ExtensionNotLoaded:
            await ctx.send(f"The extension {ext} is not loaded! (use {ctx.prefix}load)")
        except commands.NoEntryPointError:
            await ctx.send(
                f"The extension {ext} doesn't have an entry point (try adding the setup function) "
            )
        except commands.ExtensionFailed:
            await ctx.send(
                f"Some unknown error happened while trying to reload extension {ext} (check logs)"
            )
            self.bot.logger.exception(f"Failed to reload extension {ext}:")

    @commands.command(name="load", hidden=True, usage="<extension>")
    @commands.check(is_mod)
    async def _load(self, ctx, ext):
        """Loads an extension"""
        try:
            self.bot.load_extension(f"cogs.{ext}")
            await ctx.send(f"The extension {ext} was loaded!")
        except commands.ExtensionNotFound:
            await ctx.send(f"The extension {ext} doesn't exist!")
        except commands.ExtensionAlreadyLoaded:
            await ctx.send(f"The extension {ext} is already loaded.")
        except commands.NoEntryPointError:
            await ctx.send(
                f"The extension {ext} doesn't have an entry point (try adding the setup function)"
            )
        except commands.ExtensionFailed:
            await ctx.send(
                f"Some unknown error happened while trying to reload extension {ext} (check logs)"
            )
            self.bot.logger.exception(f"Failed to reload extension {ext}:")

    @commands.command(name="unload", hidden=True, usage="<extension>")
    @commands.check(is_mod)
    async def _unload(self, ctx, ext):
        """Loads an extension"""
        try:
            self.bot.unload_extension(f"cogs.{ext}")
            await ctx.send(f"The extension {ext} was unloaded!")
        except commands.ExtensionNotFound:
            await ctx.send(f"The extension {ext} doesn't exist!")
        except commands.NoEntryPointError:
            await ctx.send(
                f"The extension {ext} doesn't have an entry point (try adding the setup function)"
            )
        except commands.ExtensionFailed:
            await ctx.send(
                f"Some unknown error happened while trying to reload extension {ext} (check logs)"
            )
            self.bot.logger.exception(f"Failed to unload extension {ext}:")

    @commands.command()
    @commands.check(is_mod)
    async def activity(self, ctx, *, activity=None):
        """Change the bot's activity"""
        if activity:
            game = discord.Game(activity)
        else:
            activity = "Mining away"
            game = discord.Game(activity)
        await self.bot.change_presence(activity=game)
        await ctx.send(f"Activity changed to {activity}")


def setup(bot):
    bot.add_cog(Admin(bot))

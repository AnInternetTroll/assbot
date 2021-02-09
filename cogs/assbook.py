from hashlib import sha256
from discord.ext import commands
import discord
import json
import base64
import os

class Assbook(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.base_url: str = bot.config["assbook"]["base_url"]
        if not os.path.exists("./users.json"):
            with open("./users.json", "w") as f:
                self.users = {}
                json.dump(self.users, f)
        else:
            with open("./users.json") as f:
                self.users = json.load(f)

    @commands.command()
    async def user(self, ctx, *, user: str = None):
        if not user and self.users[str(ctx.author.id)]:
            async with self.bot.session.get(
                f"{self.base_url}/user",
                headers={"Authorization": self.users[str(ctx.author.id)]["encoded"]},
            ) as r:
                user = await r.json()
        else:
            async with self.bot.session.get(f"{self.base_url}/users/{user}") as r:
                user = await r.json()

        embed = discord.Embed(description=user["bio"])
        embed.add_field(name="ID", value=user["id"])
        embed.set_author(name=user["username"])
        await ctx.reply(embed=embed)

    @commands.command(name="users")
    async def _users(self, ctx):
        async with self.bot.session.get(f"{self.base_url}/users/") as r:
            users = await r.json()
            embed = discord.Embed(title="Users")
            for user in users:
                embed.add_field(name=user["username"], value=user["bio"])
            await ctx.reply(embed=embed)

    @commands.command(aliases=["blogs"])
    async def blog(self, ctx, user="", *, blog: str = None):
        if blog:
            async with self.bot.session.get(
                f"{self.base_url}/blogs/{user}/{blog}"
            ) as r:
                blog = await r.json()
                embed = discord.Embed(description=blog["data"])
                embed.add_field(name="ID", value=blog["id"])
                embed.set_author(name=blog["name"])
                await ctx.reply(embed=embed)
        else:
            async with self.bot.session.get(f"{self.base_url}/blogs/{user}") as r:
                blogs = await r.json()
                embed = discord.Embed(title=f"Blogs {f'from {user}' if user else ''}")
                for blog in blogs:
                    embed.add_field(name=blog["name"], value=blog["data"])
                await ctx.reply(embed=embed)

    @commands.command()
    async def post(
        self, ctx, name: str, short_name: str, description: str, *, data: str
    ):
        async with self.bot.session.post(
            f"{self.base_url}/blogs",
            data=json.dumps(
                {
                    "name": name,
                    "short_name": short_name,
                    "description": description,
                    "data": data,
                }
            ),
            headers={
                "Authorization": self.users[str(ctx.author.id)]["encoded"],
                "Content-Type": "application/json",
            },
            raise_for_status=False,
        ):
            await self.blog(
                ctx=ctx,
                user=self.users[str(ctx.author.id)]["username"],
                blog=short_name,
            )

    @commands.command()
    async def login(self, ctx: commands.Context, username: str, *, password: str):
        password = sha256(password.encode("utf-8")).hexdigest()
        encoded = f'Basic {base64.b64encode(f"{username}:{password}".encode("ascii")).decode("utf-8")}'
        async with self.bot.session.get(
            f"{self.base_url}/login", headers={"Authorization": encoded}
        ):
            self.users[str(ctx.author.id)] = {
                "username": username,
                "password": password,
                "encoded": encoded,
            }
            with open("./users.json", "w") as f:
                json.dump(self.users, f)

            await ctx.reply(
                f"```json\n{json.dumps(self.users[str(ctx.author.id)], indent=4)}```"
            )


def setup(bot):
    bot.add_cog(Assbook(bot))

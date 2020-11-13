import time
import aioredis
import aiohttp
import discord
from discord.ext import commands, tasks

from bot.bot import Bot
from bot.utils.checks import is_dev
from config.config import name

RESTART = (True, 776630056688287745)


class General(commands.Cog):
    """A general purpose cog for tasks such as cog loading"""

    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.group(name="cogs")
    @is_dev()
    async def cogs_group(self, ctx: commands.Context):
        """Perform actions such as reloading cogs"""
        if ctx.invoked_subcommand is None:
            await ctx.send(f"Usage: `!cogs <load | reload | unload> [list of cogs]`")

    @cogs_group.command(name="load")
    async def load_cogs(self, ctx: commands.Context, *cognames):
        """Load a set of cogs"""
        log = ""
        for cog in cognames:
            cog = "bot.cogs." + cog
            try:
                self.bot.load_extension(cog)
                log += f"Successfully loaded cog {cog}\n"
            except Exception as e:
                log += f"Failed to load cog {cog}: {e}\n"
                self.bot.logger.error(f"Cog loading: failed to load {cog}: {e}")

        self.bot.logger.info(f"Loaded cog(s):\n{log}")
        await ctx.send(log)

    @cogs_group.command(name="reload")
    async def reload_cogs(self, ctx: commands.Context, *cognames):
        """Reload a set of cogs"""
        log = ""
        for cog in cognames:
            cog = "bot.cogs." + cog
            try:
                self.bot.reload_extension(cog)
                log += f"Successfully reloaded cog {cog}\n"
            except Exception as e:
                log += f"Failed to reload cog {cog}: {e}\n"
                self.bot.logger.error(f"Cog reloading: failed to reload {cog}: {e}")

        self.bot.logger.info(f"Reloaded cog(s):\n{log}")
        await ctx.send(log)

    @cogs_group.command(name="unload")
    async def unload_cogs(self, ctx: commands.Context, *cognames):
        """Unload a set of cogs - you cannot unload utility.general"""
        log = ""
        for cog in cognames:
            cog = "bot.cogs." + cog
            try:
                if cog == "bot.cogs.utility.general":
                    raise Exception("You cannot unload this cog!")
                self.bot.unload_extension(cog)
                log += f"Successfully unloaded cog {cog}\n"
            except Exception as e:
                log += f"Failed to unload cog {cog}: {e}\n"
                self.bot.logger.error(f"Cog unloading: failed to unload {cog}: {e}")

        self.bot.logger.info(f"Unloaded cog(s):\n{log}")
        await ctx.send(log)

    @commands.command(name="restart", aliases=["reboot", "shutdown"])
    @is_dev()
    async def restart(self, ctx: commands.Context):
        """Make the bot logout"""
        await ctx.send("Restarting...")
        self.bot.logger.info(f"Shutting down {name}")
        await self.bot.close()

    @commands.command(name="ping")
    @is_dev()
    async def ping(self, ctx: commands.Context):
        t_start = time.time()
        m = await ctx.channel.send("Testing RTT for message editing.")
        await m.edit(content="Testing...")
        rtt = time.time() - t_start
        await m.edit(
            content=f"Pong!\nMessage edit RTT: {round(rtt * 1000, 2)}ms\nWebsocket Latency: {round(self.bot.latency * 1000, 2)}ms")

    @commands.group(name="redis", aliases=["r"])
    @is_dev()
    async def redis_g(self, ctx: commands.Context):
        pass

    @redis_g.command(name="set")
    async def redis_set(self, ctx: commands.context, key: str, *, value: str):
        await self.bot.redis.execute("set", "ctf" + key, value)
        await ctx.send(f"OK: {key}: {value}")

    @redis_g.command(name="get")
    async def redis_get(self, ctx: commands.Context, key: str):
        data = await self.bot.redis.execute("get", "ctf" + key)
        if data:
            await ctx.send(f"OK: {data.decode('utf-8')}")
            return
        await ctx.send(f"NOTOK: Query returned None.")

    @redis_g.command(name="raw")
    async def redis_raw(self, ctx: commands.Context, *args):
        args = list(args)
        try:
            data = await self.bot.redis.execute(args.pop(0), *args)
        except Exception as e:
            await ctx.send(str(e))
            return
        await ctx.send(str(data))

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.logger.info(f"{name} has started")
        await self.bot.change_presence(activity=discord.Game(name=f"Online! | {round(self.bot.latency * 1000, 3)}ms"))
        self.website_status_check.start()

        if not hasattr(self.bot, "redis"):
            self.bot.redis = await aioredis.create_connection("redis://localhost:6379")

    @commands.Cog.listener()
    async def on_message(self, m):
        if RESTART[0] and m.channel.id == RESTART[1]:
            self.bot.logger.info("Auto restarting due to git push event.")
            await self.bot.change_presence(activity=discord.Game(name="Restarting..."))
            await self.bot.logout()

    @tasks.loop(seconds=30)
    async def website_status_check(self):
        async with aiohttp.ClientSession() as sess:
            resp = await sess.get("https://ctf.vcokltf.re/ping")
            try:
                data = await resp.json()
                self.bot.logger.info("WebStatus: Success!")
                await self.bot.change_presence(activity=discord.Game(name=f"Online! | {round(self.bot.latency * 1000, 3)}ms"))
            except:
                self.bot.logger.info("WebStatus: Failed!")
                await self.bot.change_presence(activity=discord.Game(name="WEBSITE DOWN"))


def setup(bot: Bot):
    bot.add_cog(General(bot))

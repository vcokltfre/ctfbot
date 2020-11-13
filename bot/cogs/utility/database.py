import asyncio
import aiomysql
from aioredis.pubsub import Receiver
from discord.ext import commands

from bot.bot import Bot
from bot.utils.checks import is_dev
from config.config import maria

def argparse(possible: list, text: str):
    possible = [f"--{p}" for p in possible]
    args = []
    for arg in possible:
        if arg in text:
            args.append(arg.replace("--", ""))
            text.replace(arg, "")
    return args, text


class Database(commands.Cog):
    """Database commands"""

    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        if not hasattr(self.bot, "pool"):
            try:
                self.bot.pool = await aiomysql.create_pool(**maria, loop=asyncio.get_event_loop())
                self.bot.logger.info("MariaDB Connected!")
            except Exception as e:
                self.bot.logger.error(f"MariaDB: {e}")

    @commands.command(name="db")
    @is_dev()
    async def db(self, ctx: commands.Context, *, query: str):
        args, query = argparse(["desc", "all"], query)
        async with self.bot.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query)
                if "desc" in args:
                    await ctx.send(cur.description)
                    return
                if "all" in args:
                    r = await cur.fetchall()
                    await ctx.send("```py\n" + '\n'.join('{}: {}'.format(*k) for k in enumerate(r)) + "```")
                    return
                (r,) = await cur.fetchone()
                await ctx.send(r)


def setup(bot: Bot):
    bot.add_cog(Database(bot))

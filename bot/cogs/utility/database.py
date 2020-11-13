import asyncio
import aiomysql
from aioredis.pubsub import Receiver
from discord.ext import commands

from bot.bot import Bot
from bot.utils.checks import is_dev
from config.config import maria


class Database(commands.Cog):
    """Database commands"""

    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        if not hasattr(self.bot, "pool"):
            self.bot.pool = await aiomysql.create_pool(**maria, loop=asyncio.get_event_loop())

    @commands.command(name="db")
    @is_dev()
    async def db(self, ctx: commands.Context, *, query: str):
        async with self.bot.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query)
                (r,) = await cur.fetchone()
                await ctx.send(r)


def setup(bot: Bot):
    bot.add_cog(Database(bot))

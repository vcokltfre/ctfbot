import asyncio
import aiomysql
import discord
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
            text = text.replace(arg, "")
            args.append(arg.replace("--", ""))
    return args, text


class Database(commands.Cog):
    """Database commands"""

    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        if not hasattr(self.bot, "pool"):
            for i in range(3):
                try:
                    self.bot.pool = await aiomysql.create_pool(**maria, loop=asyncio.get_event_loop(), autocommit=True)
                    self.bot.logger.info("MariaDB Connected!")
                    break
                except Exception as e:
                    if i < 2:
                        self.bot.logger.error(f"MariaDB: {e}")
                    else:
                        self.bot.logger.critical("MariaDB refused to connect 3 times. Restart.")
                        await self.bot.change_presence(activity=discord.Game(name="Restarting..."))
                        await self.bot.logout()

    @commands.command(name="db")
    @is_dev()
    async def db(self, ctx: commands.Context, *, query: str):
        args, query = argparse(["desc", "one"], query)
        async with self.bot.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query)
                #await conn.commit()
                if "desc" in args:
                    await ctx.send(cur.description)
                    return
                if "one" in args:
                    (r,) = await cur.fetchone()
                    await ctx.send(r)
                    return
                r = await cur.fetchall()
                text = "```py\n" + '\n'.join('{}: {}'.format(*k) for k in enumerate(r)) + "```"
                await ctx.send(text[:1999])


def setup(bot: Bot):
    bot.add_cog(Database(bot))

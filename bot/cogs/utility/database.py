import asyncio
import aiomysql
import discord
import traceback
from discord.ext import commands, tasks
from discord.utils import get
from collections import defaultdict

from bot.bot import Bot
from bot.utils.checks import is_dev
from bot.utils.roles import get_add_remove, get_rolemap
from bot.utils.const import GET_UR, GET_ROLES
from bot.utils.utils import argparse
from bot.utils.paginate import paginate
from config.config import maria


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
                await asyncio.sleep(2)
        self.update_roles_task.start()

    @commands.command(name="db")
    @is_dev()
    async def db(self, ctx: commands.Context, *, query: str):
        args, query = argparse(["desc", "one"], query)
        async with self.bot.pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.execute(query)
                    if "desc" in args:
                        await ctx.send(cur.description)
                        return
                    if "one" in args:
                        (r,) = await cur.fetchone()
                        await ctx.send(r)
                        return
                    r = await cur.fetchall()
                    lines = ['{}: {}'.format(*k) for k in enumerate(r)]
                    pages = paginate(lines)
                    n = len(pages) if len(pages) <= 5 else 5
                    for i in range(n):
                        await ctx.send(pages[i])
                except:
                    await ctx.send(f"```\n{traceback.format_exc(limit=1950)}```")

    @tasks.loop(seconds=60)
    async def update_roles_task(self):
        async with self.bot.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(GET_ROLES) # Get list of all ctf roles ('rid',)
                r = await cur.fetchall()
                r = [int(r[0]) for r in r]

                await cur.execute(GET_UR) # Get list of users and ctf roles they should have (iuid, 'uid', 'rid',)
                u = await cur.fetchall()

                await self.update_roles(r, u) # Update the users with the roles required

    async def update_roles(self, roleids: tuple, userinfo: tuple):
        guild = get(self.bot.guilds, id=776588050276024371)

        users = defaultdict(list)
        for _, uid, rid in userinfo:
            uid = int(uid)
            user = get(guild.members, id=uid)

            if user:
                if rid is None:
                    users[user] = []
                    continue

                rid = int(rid)
                users[user].append(rid)

        for user, roles in users.items():
            try:
                cur = [r.id for r in user.roles]
                a, r = get_add_remove(cur, roleids, roles, get_rolemap(guild))
                await self.update_user_roles(user, a, r)
            except Exception as e:
                self.bot.logger.error(f"AutoRole: {traceback.format_exc(limit=1970)}")

    async def update_user_roles(self, user: discord.Member, add: list, remove: list):
        if add or remove:
            if add: await user.add_roles(*add)
            if remove: await user.remove_roles(*remove)
            self.bot.logger.info(f"AutoRole({user}): Added: {', '.join([role.name for role in add])} | Removed: {', '.join([role.name for role in remove])}")


def setup(bot: Bot):
    bot.add_cog(Database(bot))

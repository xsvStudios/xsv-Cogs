import discord
import time
from typing import Optional

from redbot.core import commands, checks
from redbot.core.utils import chat_formatting as chat

class EveTools(commands.Cog):
    """
    Eve Tools
    """
    __author__ = ["Blynd"]
    __version__ = "1.0.0"

    def __init__(self, bot):
        self.bot = bot

    def format_help_for_context(self, ctx: commands.Context) -> str:
        """
            Thanks Sinbad!
        """
        pre_processed = super().format_help_for_context(ctx)
        return f"{pre_processed}\n\nCog Version: {self.__version__}"

# Peplaces the base ping command of Red.

    @commands.cooldown(rate=1, per=2, type=commands.BucketType.user)
    @commands.bot_has_permissions(embed_links=True)
    @commands.command()
    async def ping(self, ctx):
        """Reply with latency of bot"""
        latency = self.bot.latency * 1000
        emb = discord.Embed(title="Pong ! \N{TABLE TENNIS PADDLE AND BALL} ", color=discord.Color.red())
        emb.add_field(
            name="API:", value=chat.box(str(round(latency)) + " ms"),
        )
        emb.add_field(name="Message:", value=chat.box("…"))
        emb.add_field(name="Typing:", value=chat.box("…"))

        before = time.monotonic()
        message = await ctx.send(embed=emb)
        ping = (time.monotonic() - before) * 1000
        # Thanks preda, but i copied this from MAX's version, and fixator have made it even better.
        if len(self.bot.latencies) > 1:
            # The chances of this in near future is almost 0, but who knows, what future will bring to us?
            shards = [
                f"Shard {shard + 1}/{self.bot.shard_count}: {round(pingt * 1000)}ms"
                for shard, pingt in self.bot.latencies
            ]
            emb.add_field(name="Shards:", value=chat.box("\n".join(shards)))
        emb.colour = await ctx.embed_color()
        emb.set_field_at(
            1,
            name="Message:",
            value=chat.box(
                str(int((message.created_at - ctx.message.created_at).total_seconds() * 1000))
                + " ms"
            ),
        )
        emb.set_field_at(2, name="Typing:", value=chat.box(str(round(ping)) + " ms"))

        await message.edit(embed=emb)


# Command Editor.
# This adds a listener to bot to look for message edit if a command is mistyped.
    @commands.command()
    @checks.is_owner()
    async def commandedit(self, ctx, *, timeout: float):
        """
        Edit a typo command

        Default = 5
        Disable = 0
        """
        if timeout < 0:
            timeout = 0
        await self.config.timeout.set(timeout)
        self.timeout = timeout
        await ctx.tick()

    @listener()
    async def on_message_edit(self, before, after):
        if not after.edited_at:
            return
        if before.content == after.content:
            return
        if self.timeout is None:
            self.timeout = await self.config.timeout()
        if (after.edited_at - after.created_at).total_seconds() > self.timeout:
            return
        await self.bot.process_commands(after)
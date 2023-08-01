import nextcord
from nextcord.ext import commands
from modules.storage.firebase import FirebaseStorage


# convert code into a cog
class Personality(commands.Cog):
    def __init__(
        self,
        bot: commands.Bot,
        storage: FirebaseStorage,
    ):
        self.bot = bot
        self.default_system_message = storage.child("system_message").child("default")
        self.dm_system_messages = storage.child("system_message").child("dm")
        self.guild_system_messages = storage.child("system_message").child("guild")

    @commands.group(name="personality")
    async def personality(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @personality.command(name="set")
    async def set(self, ctx: commands.Context, *, message: str):
        # check if is in DMs
        if isinstance(ctx.channel, nextcord.DMChannel):
            self.dm_system_messages[str(ctx.author.id)] = message
            await ctx.send(f"System message set to: {message}")
            return
        # channel_system_messages = self.guild_system_messages.get(str(ctx.guild.id), {})
        channel_system_messages = self.guild_system_messages[str(ctx.guild.id)] or {}
        channel_system_messages[str(ctx.channel.id)] = message
        self.guild_system_messages[str(ctx.guild.id)] = channel_system_messages

        await ctx.send(f"System message set to: {message}")

    @personality.command(name="get")
    async def get(self, ctx: commands.Context):
        # check if is in DMs
        if isinstance(ctx.channel, nextcord.DMChannel):
            current_system = (
                self.dm_system_messages[str(ctx.author.id)]
                or self.default_system_message
            )
            await ctx.send(f"System message: {current_system}")
            return

        current_system = (
            self.guild_system_messages.child(str(ctx.guild.id))[str(ctx.channel.id)]
            or self.default_system_message
        )
        await ctx.send(f"System message: {current_system}")

    @personality.command(name="clear")
    async def clear(self, ctx: commands.Context):
        # check if is in DMs
        if isinstance(ctx.channel, nextcord.DMChannel):
            self.dm_system_messages[str(ctx.author.id)] = self.default_system_message
            await ctx.send(f"System message cleared.")
            return
        #
        self.guild_system_messages.child(str(ctx.guild.id))[
            str(ctx.channel.id)
        ] = "You are a helpful AI Discord bot."
        await ctx.send(f"System message cleared.")

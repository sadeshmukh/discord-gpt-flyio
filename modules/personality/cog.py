import nextcord
from nextcord.ext import commands
from modules.storage.firebase import FirebaseStorage


class Personality(commands.Cog):
    def __init__(
        self,
        bot: commands.Bot,
        storage: FirebaseStorage,
    ):
        self.bot = bot
        self.default_system_message = storage.child("system").child("default")
        self.dm_system_messages = storage.child("system").child("dm")
        self.guild_system_messages = storage.child("system").child("guild")

    @nextcord.slash_command(name="personality", description="Personality commands")
    async def personality(self, interaction: nextcord.Interaction):
        pass

    @personality.subcommand(
        name="set",
        description="Set personality message",
    )
    async def set(self, interaction: nextcord.Interaction, *, message: str):
        # check if is in DMs
        if isinstance(interaction.channel, nextcord.DMChannel):
            self.dm_system_messages[str(interaction.user.id)] = message
            await interaction.response.send_message(f"System message set to: {message}")
            return
        # channel_system_messages = self.guild_system_messages.get(str(ctx.guild.id), {})
        channel_system_messages = (
            self.guild_system_messages[str(interaction.guild.id)] or {}
        )
        channel_system_messages[str(interaction.channel.id)] = message
        self.guild_system_messages[str(interaction.guild.id)] = channel_system_messages

        await interaction.response.send_message(f"System message set to: {message}")

    @personality.subcommand(name="get", description="Get personality message")
    async def get(self, interaction: nextcord.Interaction):
        # check if is in DMs
        if isinstance(interaction.channel, nextcord.DMChannel):
            current_system = (
                self.dm_system_messages[str(interaction.user.id)]
                or self.default_system_message.value
            )
            await interaction.response.send_message(f"System message: {current_system}")
            return

        current_system = (
            self.guild_system_messages.child(str(interaction.guild.id))[
                str(interaction.channel.id)
            ]
            or self.default_system_message.value
        )
        await interaction.response.send_message(f"System message: {current_system}")

    @personality.subcommand(name="clear", description="Reset personality message")
    async def clear(self, interaction: nextcord.Interaction):
        # check if is in DMs
        if isinstance(interaction.channel, nextcord.DMChannel):
            self.dm_system_messages[
                str(interaction.user.id)
            ] = self.default_system_message
            await interaction.response.send_message(f"System message cleared.")
            return

        self.guild_system_messages.child(str(interaction.guild.id))[
            str(interaction.channel.id)
        ] = "You are a helpful AI Discord bot."
        await interaction.response.send_message(f"System message cleared.")

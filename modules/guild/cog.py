# Set of commands that are used by server admins to configure the bot.

# Path: modules/guild/cog.py

from modules.storage.firebase import FirebaseStorage
from nextcord.ext import commands
import nextcord


class Guild(commands.Cog):
    def __init__(
        self,
        bot: commands.Bot,
        storage: FirebaseStorage,
    ):
        self.bot = bot
        self.storage = storage
        self.bot_channels = storage.child("bot_channel").child("guild")
        self.default_bot_channel = storage.child("bot_channel").child("default")

    @nextcord.slash_command(name="guild", description="Guild commands")
    async def guild(self, interaction: nextcord.Interaction):
        pass

    async def validate(self, user: nextcord.User, guild: nextcord.Guild):
        return guild.get_member(user.id).guild_permissions.manage_channels

    # add guild bot channel
    @guild.subcommand(
        name="add_bot_channel",
        description="Add bot channel",
    )
    async def add_bot_channel(
        self,
        interaction: nextcord.Interaction,
        channel: nextcord.TextChannel,
    ):
        if not await self.validate(interaction.user, interaction.guild):
            await interaction.response.send_message(
                "You do not have permission to use this command."
            )
            return
        current_bot_channels: list[nextcord.TextChannel] = self.bot_channels[
            str(interaction.guild.id)
        ]
        if not current_bot_channels:
            current_bot_channels = []
        if channel in current_bot_channels:
            await interaction.response.send_message(
                f"{channel.mention} is already a bot channel."
            )
            return
        current_bot_channels.append(str(channel.id))
        self.bot_channels[str(interaction.guild.id)] = current_bot_channels
        await interaction.response.send_message(
            f"{channel.mention} added as bot channel."
        )

    # remove guild bot channel
    @guild.subcommand(
        name="remove_bot_channel",
        description="Remove bot channel",
    )
    async def remove_bot_channel(
        self, interaction: nextcord.Interaction, channel: nextcord.TextChannel
    ):
        if not await self.validate(interaction.user, interaction.guild):
            await interaction.response.send_message(
                "You do not have permission to use this command."
            )
            return
        if not str(channel.id) in (
            self.bot_channels.child(str(interaction.guild.id)).value or []
        ):
            await interaction.response.send_message(
                f"{channel.mention} is not a bot channel."
            )
            return
        current = self.bot_channels.child(str(interaction.guild.id)).value
        current.remove(str(channel.id))
        self.bot_channels[str(interaction.guild.id)] = current

        await interaction.response.send_message(
            f"{channel.mention} removed as bot channel."
        )

    # get guild bot channels
    @guild.subcommand(
        name="get_bot_channel",
        description="Get bot channel",
    )
    async def get_bot_channel(self, interaction: nextcord.Interaction):
        if not await self.validate(interaction.user, interaction.guild):
            await interaction.response.send_message(
                "You do not have permission to use this command."
            )
            return
        current_bot_channel: list[nextcord.TextChannel] = self.bot_channels[
            str(interaction.guild.id)
        ]
        if not current_bot_channel:
            await interaction.response.send_message(
                f"No bot channel set. Default bot channel: #gpt-chat"
            )
            return

        await interaction.response.send_message(
            f"Bot channel: \n"
            + "\n".join(
                [
                    interaction.guild.get_channel(int(channel)).mention
                    for channel in current_bot_channel
                ]
            )
        )

    # clear guild bot channel
    @guild.subcommand(
        name="clear_bot_channel",
        description="Clear bot channel",
    )
    async def clear_bot_channel(self, interaction: nextcord.Interaction):
        if not await self.validate(interaction.user, interaction.guild):
            await interaction.response.send_message(
                "You do not have permission to use this command."
            )
            return
        self.bot_channels.child(str(interaction.guild.id)).delete()
        await interaction.response.send_message(f"Bot channels cleared")

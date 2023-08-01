import nextcord
from nextcord.ext import commands
from modules.storage.firebase import FirebaseStorage


class Admin(commands.Cog):
    def __init__(
        self,
        bot: commands.Bot,
        storage: FirebaseStorage,
    ):
        self.bot = bot
        self.user_usage = storage.child("usage").child("user")
        self.global_usage = storage.child("usage").child("global")
        self.user_limit = storage.child("limits").child("user")
        self.global_limit = storage.child("limits").child("global")

    async def is_authorized(self, user: nextcord.User):
        return user.id == 892912043240333322

    @nextcord.slash_command(name="admin", description="Admin commands")
    async def admin(self, ctx):
        pass

    @admin.subcommand(name="resetusage", description="Reset all token usage")
    async def reset_usage(self, interaction: nextcord.Interaction):
        if self.is_authorized(interaction.user):
            self.global_usage.set(0)
            self.user_usage.set({})
            await interaction.response.send_message("Token usage reset.")
        else:
            await interaction.response.send_message("You can't do that!")

    @admin.subcommand(name="resetuserusage", description="Reset user token usage")
    async def reset_user_usage(
        self, interaction: nextcord.Interaction, user: nextcord.User
    ):
        if self.is_authorized(interaction.user):
            self.user_usage[str(user.id)] = 0
            await interaction.response.send_message(
                f"Token usage for <@{user.id}> reset."
            )
        else:
            await interaction.response.send_message("You can't do that!")

    @admin.subcommand(name="globalusage", description="Get global token usage")
    async def get_global_usage(self, interaction: nextcord.Interaction):
        if self.is_authorized(interaction.user):
            await interaction.response.send_message(
                f"Global token usage: {self.global_usage.value}"
            )
        else:
            await interaction.response.send_message("You can't do that!")

    @admin.subcommand(name="shutdown", description="Shutdown the bot")
    async def shutdown(self, interaction: nextcord.Interaction):
        if self.is_authorized(interaction.user):
            await interaction.response.send_message("Shutting down...")
            await self.bot.close()
        else:
            await interaction.response.send_message("You can't do that!")

    @admin.subcommand(name="userlimit", description="Set user limit")
    async def set_user_limit(self, interaction: nextcord.Interaction, limit: int):
        if self.is_authorized(interaction.user):
            self.user_limit.set(limit)
            await interaction.response.send_message(f"User limit set to {limit}.")
        else:
            await interaction.response.send_message("You can't do that!")

    @admin.subcommand(name="globallimit", description="Set global limit")
    async def set_global_limit(self, interaction: nextcord.Interaction, limit: int):
        if self.is_authorized(interaction.user):
            self.global_limit.set(limit)
            await interaction.response.send_message(f"Global limit set to {limit}.")
        else:
            await interaction.response.send_message("You can't do that!")

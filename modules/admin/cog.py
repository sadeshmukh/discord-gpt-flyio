import nextcord
from nextcord.ext import commands
from modules.storage.firebase import FirebaseStorage


admin_guilds = [
    int(i) for i in FirebaseStorage("admin").child("guilds").value
]  # requires restart after update
admin_users = [
    int(i) for i in FirebaseStorage("admin").child("users").value
]  # requires restart after update

print(admin_guilds, admin_users)


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
        return user.id in admin_users

    @nextcord.slash_command(
        name="admin", description="Admin commands", guild_ids=admin_guilds
    )
    async def admin(self, ctx):
        pass

    @admin.subcommand(name="resetusage", description="Reset all token usage")
    async def reset_usage(self, interaction: nextcord.Interaction):
        if await self.is_authorized(interaction.user):
            self.global_usage.set(0)
            self.user_usage.set({})
            await interaction.response.send_message(
                "Token usage reset.", ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "You can't do that!", ephemeral=True
            )

    @admin.subcommand(name="resetuserusage", description="Reset user token usage")
    async def reset_user_usage(
        self, interaction: nextcord.Interaction, user: nextcord.User
    ):
        if await self.is_authorized(interaction.user):
            self.user_usage[str(user.id)] = 0
            await interaction.response.send_message(
                f"Token usage for <@{user.id}> reset."
            )
        else:
            await interaction.response.send_message(
                "You can't do that!", ephemeral=True
            )

    @admin.subcommand(name="globalusage", description="Get global token usage")
    async def get_global_usage(self, interaction: nextcord.Interaction):
        if await self.is_authorized(interaction.user):
            await interaction.response.send_message(
                f"Global token usage: {self.global_usage.value}", ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "You can't do that!", ephemeral=True
            )

    @admin.subcommand(name="shutdown", description="Shutdown the bot")
    async def shutdown(self, interaction: nextcord.Interaction):
        if await self.is_authorized(interaction.user):
            await interaction.response.send_message("Shutting down...")
            await self.bot.close()
        else:
            await interaction.response.send_message(
                "You can't do that!", ephemeral=True
            )

    @admin.subcommand(name="userlimit", description="Set user limit")
    async def set_user_limit(self, interaction: nextcord.Interaction, limit: int):
        if await self.is_authorized(interaction.user):
            self.user_limit.set(limit)
            await interaction.response.send_message(
                f"User limit set to {limit}.", ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "You can't do that!", ephemeral=True
            )

    @admin.subcommand(name="globallimit", description="Set global limit")
    async def set_global_limit(self, interaction: nextcord.Interaction, limit: int):
        if await self.is_authorized(interaction.user):
            self.global_limit.set(limit)
            await interaction.response.send_message(
                f"Global limit set to {limit}.", ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "You can't do that!", ephemeral=True
            )

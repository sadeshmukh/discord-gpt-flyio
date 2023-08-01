import nextcord
from nextcord.ext import commands
from modules.storage.firebase import FirebaseStorage


# # region Admin

#     @bot.slash_command()
#     async def admin(interaction: nextcord.Interaction):
#         pass

#     # slash command to reset all token usage (not accessible to everyone)
#     @admin.subcommand()
#     async def reset_usage(interaction: nextcord.Interaction):
#         if interaction.user.id == 892912043240333322:
#             global global_token_usage
#             global_token_usage = 0
#             user_usage.clear()
#             await interaction.response.send_message("Token usage reset.")
#         else:
#             await interaction.response.send_message("You can't do that!")

#     # slash command to reset user token usage (not accessible to everyone)
#     @admin.subcommand()
#     async def reset_user_usage(interaction: nextcord.Interaction, user: nextcord.User):
#         if interaction.user.id == 892912043240333322:
#             user_usage[user.id] = 0
#             await interaction.response.send_message(
#                 f"Token usage for <@{user.id}> reset."
#             )
#         else:
#             await interaction.response.send_message("You can't do that!")

#     # slash command to get global token usage (not accessible to everyone)
#     @admin.subcommand()
#     async def get_global_usage(interaction: nextcord.Interaction):
#         if interaction.user.id == 892912043240333322:
#             await interaction.response.send_message(
#                 f"Global token usage: {global_token_usage}", ephemeral=True
#             )
#         else:
#             await interaction.response.send_message("You can't do that!")

#     # slash command to shutdown bot (not accessible to everyone)
#     @admin.subcommand()
#     async def shutdown(interaction: nextcord.Interaction):
#         if interaction.user.id == 892912043240333322:
#             await interaction.response.send_message("Shutting down...")
#             await bot.close()
#         else:
#             await interaction.response.send_message("You can't do that!")

#     # slash command to set user limit (not accessible to everyone)
#     @admin.subcommand()
#     async def set_user_limit(interaction: nextcord.Interaction, limit: int):
#         if interaction.user.id == 892912043240333322:
#             global USER_LIMIT
#             USER_LIMIT = limit
#             await interaction.response.send_message(f"User limit set to {limit}.")
#         else:
#             await interaction.response.send_message("You can't do that!")

#     # slash command to set global limit (not accessible to everyone)
#     @admin.subcommand()
#     async def set_global_limit(interaction: nextcord.Interaction, limit: int):
#         if interaction.user.id == 892912043240333322:
#             global GLOBAL_LIMIT
#             GLOBAL_LIMIT = limit
#             await interaction.response.send_message(f"Global limit set to {limit}.")
#         else:
#             await interaction.response.send_message("You can't do that!")

#     # get channel history (not accessible to everyone)
#     @admin.subcommand()
#     async def get_channel_history(interaction: nextcord.Interaction):
#         if interaction.user.id == 892912043240333322:
#             await interaction.response.send_message(
#                 str(
#                     guild_chat_history.get(str(interaction.guild.id), {}).get(
#                         str(interaction.channel.id), []
#                     )
#                 )
#             )

#     # endregion


# convert code into a cog (keep admin commands in group)
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

    @commands.group()
    async def admin(self, ctx):
        pass

    @admin.command()
    async def reset_usage(self, ctx):
        if ctx.author.id == 892912043240333322:
            self.global_usage.set(0)
            self.user_usage.set({})
            await ctx.send("Token usage reset.")
        else:
            await ctx.send("You can't do that!")

    @admin.command()
    async def reset_user_usage(self, ctx, user: nextcord.User):
        if ctx.author.id == 892912043240333322:
            self.user_usage[str(user.id)] = 0
            await ctx.send(f"Token usage for <@{user.id}> reset.")
        else:
            await ctx.send("You can't do that!")

    @admin.command()
    async def get_global_usage(self, ctx):
        if ctx.author.id == 892912043240333322:
            await ctx.send(f"Global token usage: {self.global_usage.value}")
        else:
            await ctx.send("You can't do that!")

    @admin.command()
    async def shutdown(self, ctx):
        if ctx.author.id == 892912043240333322:
            await ctx.send("Shutting down...")
            await self.bot.close()
        else:
            await ctx.send("You can't do that!")

    @admin.command()
    async def set_user_limit(self, ctx, limit: int):
        if ctx.author.id == 892912043240333322:
            self.user_limit.set(limit)
            await ctx.send(f"User limit set to {limit}.")
        else:
            await ctx.send("You can't do that!")

    @admin.command()
    async def set_global_limit(self, ctx, limit: int):
        if ctx.author.id == 892912043240333322:
            self.global_limit.set(limit)
            await ctx.send(f"Global limit set to {limit}.")
        else:
            await ctx.send("You can't do that!")

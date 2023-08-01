import nextcord
from nextcord.ext import commands
from modules.storage.firebase import FirebaseStorage
import openai
import os

openai.api_key = os.environ["OPENAI_API_KEY"]

# utilities for gpt3 cog and other ai stuff - NO GROUPS


class AI(commands.Cog):
    def __init__(
        self,
        bot: commands.Bot,
        storage: FirebaseStorage,
    ):
        self.bot = bot
        self.default_system_message = storage.child("default_system_message")
        self.dm_system_messages = storage.child("dm_system_messages")
        self.guild_system_messages = storage.child("guild_system_messages")
        self.user_usage = storage.child("usage").child("user")
        self.global_usage = storage.child("usage").child("global")
        self.user_limit = storage.child("limits").child("user")
        self.global_limit = storage.child("limits").child("global")

        self.ignored_users = storage.child("ignored_users")

    async def get_response(
        self,
        history=[],
        system=None,
    ):
        if system is None:
            system = self.default_system_message
        global global_token_usage
        if global_token_usage > self.global_limit:
            return {
                "response": "Sorry, I'm out of tokens. Please try again later.",
                "usage": 0,
            }
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": system}] + history,
            temperature=0.9,
            top_p=0.95,
            max_tokens=1000,
        )
        # return token usage bundled with response, excluding everything else
        # return response.choices[0].message.content

        self.global_usage.set(self.global_usage.value + response.usage.total_tokens)
        return {
            "response": response.choices[0].message.content,
            "usage": response.usage.total_tokens,
        }

    # listen to all messages
    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message):
        if message.author == self.bot.user:
            return
        if message.author.id in self.ignored_users.value.keys():
            return

        # check for dms
        if isinstance(message.channel, nextcord.DMChannel):
            # send typing indicator
            async with message.channel.typing():
                pass
            # check if USER is over limit
            if message.author.id not in self.user_usage.value.keys():
                self.user_usage[str(message.author.id)] = 0
            if self.user_usage[str(message.author.id)] > self.user_limit.value:
                await message.channel.send(
                    f"Sorry <@{message.author.id}>, you've reached your usage limit. Please try again later."
                )
                return

            history = self.dm_chat_history[str(message.author.id)] or []
            system = (
                self.dm_system_messages[str(message.author.id)]
                or self.default_system_message.value
            )

            if len(history) > 10:
                history = history[-10:]
            history.append({"role": "user", "content": message.content})
            response = await self.get_response(history=history, system=system)
            history.append({"role": "assistant", "content": response["response"]})
            self.user_usage[str(message.author.id)] += response["usage"]
            await message.reply(response["response"], mention_author=False)

            self.dm_chat_history[str(message.author.id)] = history

            return

        # it's a guild message
        # send typing indicator
        async with message.channel.typing():
            pass
        # check if USER is over limit
        if message.author.id not in self.user_usage.value.keys():
            self.user_usage[str(message.author.id)] = 0
        if self.user_usage[str(message.author.id)] > self.user_limit.value:
            await message.channel.send(
                f"Sorry <@{message.author.id}>, you've reached your usage limit. Please try again later."
            )
            return

        # check if global over limit performed in get_response
        history = self.guild_chat_history[str(message.guild.id)] or []
        system = (
            self.guild_system_messages[str(message.guild.id)]
            or self.default_system_message.value
        )

        if len(history) > 10:
            history = history[-10:]

        history.append({"role": "user", "content": message.content})
        response = await self.get_response(history=history, system=system)
        history.append({"role": "assistant", "content": response["response"]})

        self.user_usage[str(message.author.id)] = (
            self.user_usage.value + response["usage"]
        )
        await message.reply(response["response"], mention_author=False)

    @nextcord.slash_command(name="clear", description="Clears context for a channel.")
    async def clear_context(self, interaction: nextcord.Interaction):
        if isinstance(interaction.channel, nextcord.DMChannel):
            self.dm_chat_history[str(interaction.user.id)] = []
            await interaction.response.send_message("Cleared context.")
        else:
            self.guild_chat_history.child(str(interaction.guild.id))[
                str(interaction.channel.id)
            ] = []
            await interaction.response.send_message("Cleared context.")

    @nextcord.slash_command(name="gettokens", description="Gets token usage.")
    async def get_token_usage(self, interaction: nextcord.Interaction):
        await interaction.response.send_message(
            f"Global token usage: {self.global_usage.value}"
        )
        await interaction.response.send_message(
            f"User token usage: {self.user_usage[str(interaction.user.id)]}"
        )

    @nextcord.slash_command(name="ignore", description="Toggles ignore status.")
    async def ignore(self, interaction: nextcord.Interaction):
        self.ignored_users[str(interaction.user.id)] = not self.ignored_users[
            str(interaction.user.id)
        ]
        if self.ignored_users[str(interaction.user.id)]:
            await interaction.response.send_message("You are now ignored.")
        else:
            await interaction.response.send_message("You are no longer ignored.")

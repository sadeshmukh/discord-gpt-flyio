import os
import nextcord
from nextcord.ext import commands
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")
CURRENTLY_COMPLETING = False


global_token_usage = 0
GLOBAL_LIMIT = 10000

user_usage = {}
USER_LIMIT = 1000

ignored_users = []

# dict of guilds, with each guild having a dictionary of channels, each channel having a list of messages
guild_chat_history = {}

# dict of guilds, with each guild having a dictionary of channels, each channel having a system message
guild_system_messages = {}

# dm channel history
dm_chat_history = {}

# dm channel system messages
dm_system_messages = {}

DEFAULT_SYSTEM_MESSAGE = (
    "You are a helpful Discord chatbot. Keep your responses concise."
)

# define openai interaction


async def get_response(
    history=[],
    system=DEFAULT_SYSTEM_MESSAGE,
):
    global global_token_usage
    if global_token_usage > GLOBAL_LIMIT:
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

    global_token_usage += response.usage.total_tokens
    return {
        "response": response.choices[0].message.content,
        "usage": response.usage.total_tokens,
    }


def main():
    intents = nextcord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(intents=intents)

    @bot.listen("on_ready")
    async def on_ready():
        await bot.wait_until_ready()
        await bot.change_presence(
            activity=nextcord.Activity(
                type=nextcord.ActivityType.listening, name="your messages"
            )
        )

        await bot.get_guild(1100200559807569950).get_channel(1101005585534689351).send(
            "**Bot restarted.**"
        )

        print(f"{bot.user.name} has connected to Discord.")

    # region GPT-3
    # respond to messages mentioning gpt bot, and include history of messages in channel
    @bot.listen()
    async def on_message(message: nextcord.Message):
        if message.author == bot.user:
            return
        if message.author.id in ignored_users:
            return

        # check if is in DMs

        if isinstance(message.channel, nextcord.DMChannel):
            # send typing indicator
            async with message.channel.typing():
                pass
            # check if USER is over limit
            if message.author.id not in user_usage:
                user_usage[str(message.author.id)] = 0
            if user_usage[str(message.author.id)] > USER_LIMIT:
                await message.channel.send(
                    f"Sorry <@{message.author.id}>, you've reached your usage limit. Please try again later."
                )
                return

            history = dm_chat_history.get(str(message.author.id), [])
            system = dm_system_messages.get(
                str(message.author.id), DEFAULT_SYSTEM_MESSAGE
            )

            if len(history) > 10:
                history = history[-10:]
            history.append({"role": "user", "content": message.content})
            response = await get_response(history=history, system=system)
            history.append({"role": "assistant", "content": response["response"]})
            user_usage[str(message.author.id)] += response["usage"]
            await message.reply(response["response"], mention_author=False)

            dm_chat_history[str(message.author.id)] = history

            return

        # check if one of 3 things: bot is mentioned, bot is replied to, or message is in channel "gpt-chat"

        if (
            f"<@{bot.user.id}>" in message.content
            or (message.reference and message.reference.resolved.author == bot.user)
            or message.channel.name == "gpt-chat"
        ):
            # send typing indicator
            async with message.channel.typing():
                pass
            # check if USER is over limit
            if message.author.id not in user_usage:
                user_usage[str(message.author.id)] = 0
            if user_usage[str(message.author.id)] > USER_LIMIT:
                await message.channel.send(
                    f"Sorry <@{message.author.id}>, you've reached your usage limit. Please try again later."
                )
                return

            history = guild_chat_history.get(str(message.guild.id), {}).get(
                str(message.channel.id), []
            )
            system = guild_system_messages.get(str(message.guild.id), {}).get(
                str(message.channel.id), DEFAULT_SYSTEM_MESSAGE
            )

            if len(history) > 10:
                history = history[-10:]
            history.append({"role": "user", "content": message.content})
            response = await get_response(history=history, system=system)
            history.append({"role": "assistant", "content": response["response"]})
            user_usage[str(message.author.id)] += response["usage"]
            await message.reply(response["response"], mention_author=False)
            channel_history = guild_chat_history.get(str(message.guild.id), {})
            channel_history[str(message.channel.id)] = history
            guild_chat_history[str(message.guild.id)] = channel_history

    # endregion

    # slash command to clear context in channel (accessible to everyone)
    @bot.slash_command()
    async def clear_context(interaction: nextcord.Interaction):
        guild_chat_history[interaction.guild.id][interaction.channel.id] = []
        await interaction.response.send_message(
            "Context cleared.",
        )

    # slash command to check user token usage (accessible to everyone)
    @bot.slash_command()
    async def get_token_usage(interaction: nextcord.Interaction):
        await interaction.response.send_message(
            f"Your token usage: {user_usage.get(interaction.user.id, 0)}"
        )

    # slash command to ignore self user (accessible to everyone)
    # removes user from ignored_users list if already ignored
    @bot.slash_command()
    async def ignore(interaction: nextcord.Interaction):
        if interaction.user.id in ignored_users:
            ignored_users.remove(interaction.user.id)
            await interaction.response.send_message("You are no longer ignored.")
        else:
            ignored_users.append(interaction.user.id)
            await interaction.response.send_message("You are now ignored.")

    # region Personality
    @bot.slash_command()
    async def personality(interaction: nextcord.Interaction):
        pass

    @personality.subcommand()
    async def set(interaction: nextcord.Interaction, message: str):
        # check if is in DMs
        if isinstance(interaction.channel, nextcord.DMChannel):
            dm_system_messages[str(interaction.author.id)] = message
            await interaction.response.send_message(
                f"System message set to: {message}",
            )
            return
        channel_system_messages = guild_system_messages.get(
            str(interaction.guild.id), {}
        )
        channel_system_messages[str(interaction.channel.id)] = message
        guild_system_messages[str(interaction.guild.id)] = channel_system_messages

        await interaction.response.send_message(
            f"System message set to: {message}",
        )

    @personality.subcommand()
    async def get(interaction: nextcord.Interaction):
        # check if is in DMs
        if isinstance(interaction.channel, nextcord.DMChannel):
            current_system = dm_system_messages.get(
                str(interaction.author.id), DEFAULT_SYSTEM_MESSAGE
            )
            await interaction.response.send_message(f"System message: {current_system}")
            return
        current_system = guild_system_messages.get(str(interaction.guild.id), {}).get(
            str(interaction.channel.id), DEFAULT_SYSTEM_MESSAGE
        )
        await interaction.response.send_message(f"System message: {current_system}")

    @personality.subcommand()
    async def clear(interaction: nextcord.Interaction):
        # check if is in DMs
        if isinstance(interaction.channel, nextcord.DMChannel):
            dm_system_messages[str(interaction.author.id)] = DEFAULT_SYSTEM_MESSAGE
            await interaction.response.send_message(
                f"System message cleared.",
            )
            return
        guild_system_messages[interaction.guild.id][
            interaction.channel.id
        ] = "You are a helpful AI Discord bot."
        await interaction.response.send_message(
            f"System message cleared.",
        )

    # endregion

    # region Admin

    @bot.slash_command()
    async def admin(interaction: nextcord.Interaction):
        pass

    # slash command to reset all token usage (not accessible to everyone)
    @admin.subcommand()
    async def reset_usage(interaction: nextcord.Interaction):
        if interaction.user.id == 892912043240333322:
            global global_token_usage
            global_token_usage = 0
            user_usage.clear()
            await interaction.response.send_message("Token usage reset.")
        else:
            await interaction.response.send_message("You can't do that!")

    # slash command to reset user token usage (not accessible to everyone)
    @admin.subcommand()
    async def reset_user_usage(interaction: nextcord.Interaction, user: nextcord.User):
        if interaction.user.id == 892912043240333322:
            user_usage[user.id] = 0
            await interaction.response.send_message(
                f"Token usage for <@{user.id}> reset."
            )
        else:
            await interaction.response.send_message("You can't do that!")

    # slash command to get global token usage (not accessible to everyone)
    @admin.subcommand()
    async def get_global_usage(interaction: nextcord.Interaction):
        if interaction.user.id == 892912043240333322:
            await interaction.response.send_message(
                f"Global token usage: {global_token_usage}", ephemeral=True
            )
        else:
            await interaction.response.send_message("You can't do that!")

    # slash command to shutdown bot (not accessible to everyone)
    @admin.subcommand()
    async def shutdown(interaction: nextcord.Interaction):
        if interaction.user.id == 892912043240333322:
            await interaction.response.send_message("Shutting down...")
            await bot.close()
        else:
            await interaction.response.send_message("You can't do that!")

    # slash command to set user limit (not accessible to everyone)
    @admin.subcommand()
    async def set_user_limit(interaction: nextcord.Interaction, limit: int):
        if interaction.user.id == 892912043240333322:
            global USER_LIMIT
            USER_LIMIT = limit
            await interaction.response.send_message(f"User limit set to {limit}.")
        else:
            await interaction.response.send_message("You can't do that!")

    # slash command to set global limit (not accessible to everyone)
    @admin.subcommand()
    async def set_global_limit(interaction: nextcord.Interaction, limit: int):
        if interaction.user.id == 892912043240333322:
            global GLOBAL_LIMIT
            GLOBAL_LIMIT = limit
            await interaction.response.send_message(f"Global limit set to {limit}.")
        else:
            await interaction.response.send_message("You can't do that!")

    # get channel history (not accessible to everyone)
    @admin.subcommand()
    async def get_channel_history(interaction: nextcord.Interaction):
        if interaction.user.id == 892912043240333322:
            await interaction.response.send_message(
                str(
                    guild_chat_history.get(str(interaction.guild.id), {}).get(
                        str(interaction.channel.id), []
                    )
                )
            )

    # endregion

    bot.run(os.getenv("DISCORD_TOKEN"))


if __name__ == "__main__":
    main()

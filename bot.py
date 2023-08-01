import os
import nextcord
from nextcord.ext import commands
import openai

from modules.storage.firebase import FirebaseStorage
from modules.ai.cog import AI
from modules.personality.cog import Personality
from modules.admin.cog import Admin


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

    # define FirebaseStorage object

    storage = FirebaseStorage()

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

    # import all cogs manually
    bot.add_cog(AI(bot, storage=storage))
    bot.add_cog(Personality(bot, storage=storage))
    bot.add_cog(Admin(bot, storage=storage))

    bot.run(os.getenv("DISCORD_TOKEN"))


if __name__ == "__main__":
    main()

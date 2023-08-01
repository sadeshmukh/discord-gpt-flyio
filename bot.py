import os
import nextcord
from nextcord.ext import commands
import openai

from modules.storage.firebase import FirebaseStorage
from modules.ai.cog import AI
from modules.personality.cog import Personality
from modules.admin.cog import Admin


def main():
    intents = nextcord.Intents.default()
    intents.message_content = True
    intents.guilds = True
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

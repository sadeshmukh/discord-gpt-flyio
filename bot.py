import os
import nextcord
from nextcord.ext import commands
import schedule

from modules.storage.firebase import FirebaseStorage
from modules.ai.cog import AI
from modules.personality.cog import Personality
from modules.admin.cog import Admin
from modules.guild.cog import Guild


def resetusage():
    storage = FirebaseStorage()
    current_global_usage = storage.child("usage").child("global").value
    current_user_usage = storage.child("usage").child("user").value

    storage.child("historic")["global"] = (
        storage.child("historic")["global"] or 0 + current_global_usage
    )

    for user in current_user_usage:
        storage.child("historic")["user"][user] = (
            storage.child("historic")["user"][user] or 0 + current_user_usage[user]
        )

    storage.child("usage").set({"global": 0, "user": {}})


def main():
    intents = nextcord.Intents.default()
    intents.message_content = True
    intents.guilds = True
    intents.members = True
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
    bot.add_cog(Guild(bot, storage=storage))

    schedule.every().day.at("07:00").do(resetusage)
    bot.run(os.getenv("DISCORD_TOKEN"))


if __name__ == "__main__":
    main()

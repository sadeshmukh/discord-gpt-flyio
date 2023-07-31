import os
import nextcord
from nextcord.ext import commands
import openai

# define openai interaction


def get_response(message):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"text": message}],
        temperature=0.9,
        top_p=0.95,
    )
    return response.choices[0].message.content


def main():
    bot = commands.Bot()

    @bot.event
    async def on_ready():
        await print(f"{bot.user.name} has connected to Discord.")

    # create slash command
    @bot.slash_command()
    async def hello(interaction: nextcord.Interaction):
        await interaction.response.send_message(f"Hello <@{interaction.user.id}>!")

    # slash command to shut it down, only works for me
    @bot.slash_command(guild_ids=[903144081868345355])
    async def shutdown(interaction: nextcord.Interaction):
        if interaction.user.id == 892912043240333322:
            await interaction.response.send_message("Shutting down...")
            await bot.close()
        else:
            await interaction.response.send_message("You can't do that!")

    bot.run(os.getenv("DISCORD_TOKEN"))


if __name__ == "__main__":
    main()

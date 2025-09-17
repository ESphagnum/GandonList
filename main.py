import discord
from discord.ext import commands
import os
from core.config import settings
import logging

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f"Бот {bot.user} запущен!")
    bot.load_extension('cogs.Ban.main')
    await bot.sync_commands()

@bot.event
async def on_command_error(ctx: discord.ApplicationContext, error: commands.CommandError):
    error_messages = {
        commands.MissingRole: "У вас нет роли для выполнения этой команды",
        commands.MissingAnyRole: "Вам не хватает одной из необходимых ролей",
        commands.CommandNotFound: "Команда не найдена",
        commands.CommandOnCooldown: lambda e: f"Команда на перезарядке. Подождите {round(e.retry_after, 2)} секунд",
    }

    for error_type, message in error_messages.items():
        if isinstance(error, error_type):
            error_msg = message(error) if callable(message) else message
            return await ctx.respond(
                embed=discord.Embed(title="Error", description=error_msg)
            )

    await ctx.respond(
        embed=discord.Embed(title="Error", description=f"Неизвестная ошибка: {error}")
    )
    print(error)


if __name__ == "__main__":
    try:
        print(settings.TOKEN)
        bot.run(settings.TOKEN)
    except Exception as e:
        print(f"Не удалось запустить бота: {e}")
import discord
from discord.ext import bridge, commands

import os, sys, logging

from core.config import settings


intents = discord.Intents.default()
intents.message_content = True
bot = bridge.Bot(command_prefix="!", intents=discord.Intents.all())
# logging.basicConfig(
#     format="%(asctime)s [%(levelname)s] %(message)s",
#     handlers=[
#         logging.StreamHandler(sys.stdout),
#         logging.FileHandler("logs.log", encoding="utf-8"),
#     ],
# )
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)


@bot.event
async def on_ready():
    print(f"Бот {bot.user} запущен!")
    bot.load_extension("cogs.Gandon.ban")
    bot.load_extension("cogs.Gandon.stats")
    print(bot.cogs)


@bot.bridge_command(name="sync")
@commands.has_role(settings.developer_role_id)
async def sync(ctx: discord.Interaction):
    await bot.sync_commands(guild_ids=[settings.guild_id])
    await ctx.respond("Synced", ephemeral=True)


@bot.event
async def on_command_error(
    ctx: discord.ApplicationContext, error: commands.CommandError
):
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

import discord
from discord import Option
from discord.ext import commands

from sqlalchemy import select, func, and_
from sqlalchemy.orm import aliased

from datetime import datetime, timedelta, timezone

from core.models import Player, ServerBan, AdminNotes
from core.models.db_helper import db_helper
from core.config import settings
from .dependency import extract_nickname

class StatsCog(commands.Cog):
    def __init__(self, bot, session=db_helper.get_scoped_session()):
        self.bot = bot
        self.session = session

    @commands.slash_command(
        name="top_admins", description="Топ 10 админов по количеству банов"
    )
    @commands.has_role(settings.admin_role_id)
    async def top_admins(
        self,
        ctx: discord.ApplicationContext,
        period: Option(
            str,
            "Период",
            choices=["all_time", "year", "month", "week", "day"],
            required=False,
            default="all_time",
        ) = "all_time",
    ):
        await ctx.defer(ephemeral=True)

        try:
            date_condition = self.get_date_condition(period, ServerBan.ban_time)

            async with self.session() as session:
                admin_alias = aliased(Player)

                query = (
                    select(
                        admin_alias.last_seen_user_name,
                        func.count(ServerBan.server_ban_id).label("ban_count"),
                    )
                    .join(admin_alias, ServerBan.banning_admin == admin_alias.user_id)
                    .where(date_condition)
                    .group_by(admin_alias.last_seen_user_name)
                    .order_by(func.count(ServerBan.server_ban_id).desc())
                    .limit(10)
                )

                result = await session.execute(query)

                if not (top_admins := result.all()):
                    embed = discord.Embed(
                        title=f"**Топ 10 админов ({self.get_period_name(period)})**",
                        description="Нет данных за выбранный период",
                        color=discord.Color.dark_purple(),
                    )
                else:
                    embed = discord.Embed(
                        title=f"**Топ 10 админов ({self.get_period_name(period)})**",
                        color=discord.Color.dark_purple(),
                    )
                    for i, (admin_name, ban_count) in enumerate(top_admins, 1):
                        embed.add_field(
                            name=f"{i}. {extract_nickname(admin_name)}",
                            value=f"Банов: {ban_count}",
                            inline=False,
                        )

                await ctx.respond(embed=embed, ephemeral=True)

        except Exception as e:
            await ctx.respond(f"Ошибка: {str(e)}", ephemeral=True)

    @commands.slash_command(name="stats", description="Статистика банов за период")
    @commands.has_role(settings.admin_role_id)
    async def ban_stats(
        self,
        ctx: discord.ApplicationContext,
        period: Option(
            str,
            "Период",
            choices=["all_time", "year", "month", "week", "day"],
            required=False,
            default="all_time",
        ) = "all_time",
    ):
        await ctx.defer(ephemeral=True)

        try:
            date_condition_ban = self.get_date_condition(period, ServerBan.ban_time)
            date_condition_note = self.get_date_condition(period, AdminNotes.created_at)

            async with self.session() as session:
                # Общяг банов
                total_query = select(func.count(ServerBan.server_ban_id)).where(
                    date_condition_ban
                )
                total_bans = (await session.execute(total_query)).scalar()

                # Кол-во игроков с банчиком
                unique_players_query = select(
                    func.count(func.distinct(ServerBan.player_user_id))
                ).where(date_condition_ban)
                unique_players = (await session.execute(unique_players_query)).scalar()

                # Кол-во служителей во имя добра(админов)
                active_admins_query = select(
                    func.count(func.distinct(ServerBan.banning_admin))
                ).where(date_condition_ban)
                active_admins = (await session.execute(active_admins_query)).scalar()

                # Кол-во заметок
                total_notes_query = select(func.count(AdminNotes.admin_notes_id)).where(
                    and_(date_condition_note, AdminNotes.deleted == False)
                )
                total_notes = (await session.execute(total_notes_query)).scalar()

                embed = discord.Embed(
                    title=f"**Статистика банов ({self.get_period_name(period)})**",
                    color=discord.Color.red(),
                )

                embed.add_field(
                    name="👤 Игроков", value=f"**{unique_players}**", inline=True
                )
                embed.add_field(
                    name="🛡️ Комбатантов", value=f"**{active_admins}**", inline=False
                )
                embed.add_field(name="📋Заметок", value=f"**{total_notes}**", inline=True)
                embed.add_field(
                    name="✏️ Всего банов", value=f"**{total_bans}**", inline=False
                )

                await ctx.respond(embed=embed, ephemeral=True)

        except Exception as e:
            await ctx.send(f"Ошибка: {str(e)}", ephemeral=True)

    def get_date_condition(self, period, column):
        now = datetime.now(timezone.utc)
        if period == "year":
            return column >= now - timedelta(days=365)
        elif period == "month":
            return column >= now - timedelta(days=30)
        elif period == "week":
            return column >= now - timedelta(days=7)
        elif period == "day":
            return column >= now - timedelta(days=1)
        else:  # для all_time ненядя фильтры :D
            return True

    def get_period_name(self, period):
        period_names = {
            "all_time": "все время",
            "year": "год",
            "month": "месяц",
            "week": "неделя",
            "day": "день",
        }
        return period_names.get(period, period)


def setup(bot):
    bot.add_cog(StatsCog(bot))

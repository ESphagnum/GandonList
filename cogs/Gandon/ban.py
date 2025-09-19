import discord
from discord import Option
from discord.ext import commands
from discord.ext.pages import Paginator, Page

from sqlalchemy import select, and_, or_
from sqlalchemy.orm import aliased

from datetime import datetime, timezone
import re
from typing import Optional

from core.models import Player, ServerBan
from core.models.db_helper import db_helper
from core.config import settings
from .dependency import extract_nickname


class BanCog(commands.Cog):
    def __init__(self, bot, session=db_helper.get_scoped_session()):
        self.bot = bot
        self.session = session

    @commands.slash_command(
        name="banlist", description="Поиск банов по различным критериям"
    )
    @commands.has_role(settings.admin_role_id)
    async def banlist(
        self,
        ctx: discord.ApplicationContext,
        player_name: Option(str, "Никнейм игрока", required=False) = None,
        admin_name: Option(str, "Никнейм администратора", required=False) = None,
        from_date: Option(str, "Дата начала (YYYYMMDD)", required=False) = None,
        before_date: Option(str, "Дата окончания (YYYYMMDD)", required=False) = None,
    ):
        await ctx.defer(ephemeral=True)

        try:
            async with self.session() as session:
                player_alias = aliased(Player)
                admin_alias = aliased(Player)
                edited_by_alias = aliased(Player)

                query = (
                    select(
                        ServerBan,
                        player_alias.last_seen_user_name.label("player_name"),
                        admin_alias.last_seen_user_name.label("admin_name"),
                        edited_by_alias.last_seen_user_name.label("edited_by_name"),
                    )
                    .outerjoin(
                        player_alias, ServerBan.player_user_id == player_alias.user_id
                    )
                    .outerjoin(
                        admin_alias, ServerBan.banning_admin == admin_alias.user_id
                    )
                    .outerjoin(
                        edited_by_alias,
                        ServerBan.last_edited_by_id == edited_by_alias.user_id,
                    )
                )

                filters = []
                if player_name:
                    filters.append(
                        or_(
                            player_alias.last_seen_user_name == (clean_player_name := extract_nickname(player_name)),
                            player_alias.last_seen_user_name.endswith(f"@{clean_player_name}")
                        )
                    )

                if admin_name:
                    filters.append(
                        or_(
                            admin_alias.last_seen_user_name == (clean_admin_name := extract_nickname(admin_name)),
                            admin_alias.last_seen_user_name.endswith(f"@{clean_admin_name}")
                        )
                    )
                if from_date and (from_dt := self.parse_date(from_date)):
                    filters.append(ServerBan.ban_time >= from_dt)
                if before_date and (before_dt := self.parse_date(before_date)):
                    filters.append(ServerBan.ban_time <= before_dt)

                if filters:
                    query = query.where(and_(*filters))

                query = query.order_by(ServerBan.ban_time.desc()).limit(100)
                result = await session.execute(query)
                bans = result.all()


                if not bans:
                    await ctx.respond("Баны не найдены", ephemeral=True)
                    return

                pages = []
                for ban, player_nick_raw, admin_nick_raw, edited_by_nick_raw in bans:
                    player_nickname = extract_nickname(player_nick_raw)
                    admin_nickname = extract_nickname(admin_nick_raw)
                    edited_by_nickname = extract_nickname(edited_by_nick_raw) if edited_by_nick_raw else None
                    embed = discord.Embed(
                        title=f"**Бан #{ban.server_ban_id}**",
                        color=discord.Color.red(),
                        timestamp=ban.ban_time,
                    )

                    player_display = player_nickname or f"UUID: {ban.player_id}"
                    embed.add_field(name="👤 Игрок", value=player_display, inline=True)

                    admin_display = admin_nickname or f"UUID: {ban.banning_admin}"
                    embed.add_field(name="🛡️ Админ", value=admin_display, inline=True)

                    if ban.severity and (
                        severity_list := ["Нет", "Низкий", "Средний", "Высокий"]
                    ):
                        embed.add_field(
                            name="⚡ Строгость",
                            value=severity_list[int(ban.severity)],
                            inline=True,
                        )

                    embed.add_field(
                        name="⏰ Время бана",
                        value=ban.ban_time.strftime("%Y-%m-%d %H:%M UTC"),
                        inline=True,
                    )

                    if ban.expiration_time:
                        embed.add_field(
                            name="⏳ Истекает",
                            value=ban.expiration_time.strftime("%Y-%m-%d %H:%M UTC"),
                            inline=True,
                        )

                    if ban.last_edited_at and edited_by_nickname:
                        embed.add_field(
                            name="✏️ Последнее изменение",
                            value=f"{edited_by_nickname} в {ban.last_edited_at.strftime('%Y-%m-%d %H:%M UTC')}",
                            inline=False,
                        )

                    if ban.address:
                        embed.add_field(
                            name="🌐 IP-адрес", value=str(ban.address), inline=True
                        )

                    embed.add_field(name="📝 Причина", value=ban.reason, inline=False)

                    pages.append(Page(embeds=[embed]))

                # Родненький мой, паджинотор... Где ты был в discord.py?
                paginator = Paginator(
                    pages=pages,
                    show_indicator=True,
                    show_disabled=True,
                    use_default_buttons=True,
                    loop_pages=True,
                    timeout=120,
                )

                if (ban_count := len(bans)) == 100:
                    await ctx.respond(
                        "Показаны только первые 100 банов. Уточните критерии поиска.",
                    )

                await paginator.respond(ctx, ephemeral=True)

        except ValueError as e:
            await ctx.respond(
                f"Ошибка формата даты: {str(e)}. Используйте: YYYYMMDD или YYYY-MM-DD",
                ephemeral=True,
            )
        except Exception as e:
            await ctx.respond(f"Ошибка: {str(e)}", ephemeral=True)

    def parse_date(self, date_str: str) -> Optional[datetime]:
        try:
            if (length := len(date_str)) == 8:  # YYYYMMDD
                return datetime.strptime(date_str, "%Y%m%d").replace(
                    tzinfo=timezone.utc
                )
            elif length == 10:  # YYYY-MM-DD
                return datetime.strptime(date_str, "%Y-%m-%d").replace(
                    tzinfo=timezone.utc
                )
            else:
                raise ValueError("Неверный формат даты")
        except ValueError:
            raise ValueError(
                "Неверный формат даты. Используйте: YYYYMMDD или YYYY-MM-DD"
            )

    def parse_date(self, date_str):
        if not date_str:
            return None

        try:
            if (length := len(date_str)) == 8:  # YYYYMMDD
                return datetime.strptime(date_str, "%Y%m%d").replace(
                    tzinfo=timezone.utc
                )
            elif length == 10:  # YYYY-MM-DD
                return datetime.strptime(date_str, "%Y-%m-%d").replace(
                    tzinfo=timezone.utc
                )
            else:
                raise ValueError("Неверный формат даты")
        except ValueError:
            raise ValueError(
                "Неверный формат даты. Используйте: YYYYMMDD или YYYY-MM-DD"
            )


def setup(bot):
    bot.add_cog(BanCog(bot))

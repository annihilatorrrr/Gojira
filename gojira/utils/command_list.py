# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

from aiogram import Bot
from aiogram.types import (
    BotCommand,
    BotCommandScopeAllGroupChats,
    BotCommandScopeAllPrivateChats,
)
from aiogram.utils.i18n import I18n


async def set_ui_commands(bot: Bot, i18n: I18n):
    _ = i18n.gettext

    await bot.delete_my_commands()
    for lang in i18n.available_locales:
        user_commands: list[BotCommand] = [
            BotCommand(
                command="start",
                description=_("Start the bot.", locale=lang),
            ),
            BotCommand(
                command="help",
                description=_("Get help.", locale=lang),
            ),
            BotCommand(
                command="anime",
                description=_("Get anime informations.", locale=lang),
            ),
            BotCommand(
                command="manga",
                description=_("Get manga informations.", locale=lang),
            ),
            BotCommand(
                command="language",
                description=_("Change bot language.", locale=lang),
            ),
            BotCommand(
                command="about",
                description=_("About the bot.", locale=lang),
            ),
        ]

        group_commands: list[BotCommand] = [
            BotCommand(
                command="anime",
                description=_("Get anime informations.", locale=lang),
            ),
            BotCommand(
                command="manga",
                description=_("Get manga informations.", locale=lang),
            ),
            BotCommand(
                command="language",
                description=_("Change bot language.", locale=lang),
            ),
            BotCommand(
                command="about",
                description=_("About the bot.", locale=lang),
            ),
        ]

        await bot.set_my_commands(
            user_commands,
            BotCommandScopeAllPrivateChats(type="all_private_chats"),
            language_code=lang.split("_")[0].lower() if "_" in lang else lang,
        )

        await bot.set_my_commands(
            group_commands,
            BotCommandScopeAllGroupChats(type="all_group_chats"),
            language_code=lang.split("_")[0].lower() if "_" in lang else lang,
        )

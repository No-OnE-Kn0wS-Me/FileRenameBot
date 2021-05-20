import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

import os
import time
import asyncio
import pyrogram

if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config
from translation import Translation

from pyrogram import filters
from pyrogram import Client as MaI_BoTs
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ForceReply

from helper_funcs import display_progress

from hachoir.metadata import extractMetadata
from hachoir.parser import createParser

from PIL import Image
from database.database import *

@MaI_BoTs.on_message(filters.private & (filters.document | filters.video | filters.audio | filters.voice | filters.video_note))
async def rename_cb(bot, update):
 
    file = update.document or update.video or update.audio or update.voice or update.video_note
    try:
        filename = file.file_name
    except:
        filename = "Not Available"
    
    await bot.send_message(
        chat_id=update.chat.id,
        text="<b>File Name</b> : <code>{}</code>\n\n what you Want To Do With This File? ".format(filename),
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="Rename", callback_data="rename_button")],
                                                [InlineKeyboardButton(text="Cancel", callback_data="cancel_e")]]),
        parse_mode="html",
        reply_to_message_id=update.message_id,
        disable_web_page_preview=True   
    )   
async def force_name(bot, message):

    await bot.send_message(
        message.reply_to_message.from_user.id,
        "Enter new name for media\n\nNote : Extension not required",
        reply_to_message_id=message.reply_to_message.message_id,
        reply_markup=ForceReply(True)
    )


async def cancel_extract(bot, update):
    
    await bot.send_message(
        chat_id=update.chat.id,
        text="Process Cancelled Successfully",
    )

@MaI_BoTs.on_callback_query()
async def cb_handler(bot, update):
        
    if "rename_button" in update.data:
        await update.message.delete()
        await force_name(bot, update.message)
        
    elif "cancel_e" in update.data:
        await update.message.delete()
        await cancel_extract(bot, update.message)



@MaI_BoTs.on_message(filters.private & filters.reply & filters.text)
async def cus_name(bot, message):
    
    if (message.reply_to_message.reply_markup) and isinstance(message.reply_to_message.reply_markup, ForceReply):
        asyncio.create_task(rename_doc(bot, message))     
    else:
        print('No media present')

    
async def rename_doc(bot, message):
    
    mssg = await bot.get_messages(
        message.chat.id,
        message.reply_to_message.message_id
    )    
    
    media = mssg.reply_to_message

    
    if media.empty:
        await message.reply_text('Why did you delete that 😕', True)
        return
        
    filetype = media.document or media.video or media.audio or media.voice or media.video_note
    try:
        actualname = filetype.file_name
        splitit = actualname.split(".")
        extension = (splitit[-1])
    except:
        extension = "mkv"

    await bot.delete_messages(
        chat_id=message.chat.id,
        message_ids=message.reply_to_message.message_id,
        revoke=True
    )
    
    if message.from_user.id not in Config.BANNED_USERS:
        file_name = message.text
        description = Translation.CUSTOM_CAPTION_UL_FILE.format(newname=file_name)
        download_location = Config.DOWNLOAD_LOCATION + "/"

        sendmsg = await bot.send_message(
            chat_id=message.chat.id,
            text=Translation.DOWNLOAD_START,
            reply_to_message_id=message.message_id
        )
        
        c_time = time.time()
        the_real_download_location = await bot.download_media(
            message=media,
            file_name=download_location,
            progress=display_progress,
            progress_args=(
                Translation.DOWNLOAD_START,
                sendmsg,
                c_time
            )
        )
        if the_real_download_location is not None:
            try:
                await bot.edit_message_text(
                    text=Translation.SAVED_RECVD_DOC_FILE,
                    chat_id=message.chat.id,
                    message_id=sendmsg.message_id
                )
            except:
                await sendmsg.delete()
                sendmsg = await message.reply_text(script.SAVED_RECVD_DOC_FILE, quote=True)

            new_file_name = download_location + file_name + "." + extension
            os.rename(the_real_download_location, new_file_name)
            try:
                await bot.edit_message_text(
                    text=Translation.UPLOAD_START,
                    chat_id=message.chat.id,
                    message_id=sendmsg.message_id
                    )
            except:
                await sendmsg.delete()
                sendmsg = await message.reply_text(Translation.UPLOAD_START, quote=True)
            # logger.info(the_real_download_location)

            thumb_image_path = download_location + str(message.from_user.id) + ".jpg"
            if not os.path.exists(thumb_image_path):
                mes = await thumb(message.from_user.id)
                if mes != None:
                    m = await bot.get_messages(message.chat.id, mes.msg_id)
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
                Image.open(thumb_image_path).convert("RGB").save(thumb_image_path)
                img = Image.open(thumb_image_path)
                img.resize((320, height))
                img.save(thumb_image_path, "JPEG")

            c_time = time.time()
            await bot.send_document(
                chat_id=message.chat.id,
                document=new_file_name,
                thumb=thumb_image_path,
                caption=description,
                # reply_markup=reply_markup,
                reply_to_message_id=message.reply_to_message.message_id,
                progress=display_progress,
                progress_args=(
                    Translation.UPLOAD_START,
                    sendmsg, 
                    c_time
                )
            )

            try:
                os.remove(new_file_name)
            except:
                pass                 
            try:
                os.remove(thumb_image_path)
            except:
                pass  
            try:
                await bot.edit_message_text(
                    text=Translation.AFTER_SUCCESSFUL_UPLOAD_MSG,
                    chat_id=message.chat.id,
                    message_id=sendmsg.message_id,
                    disable_web_page_preview=True
                )
            except:
                await sendmsg.delete()
                await message.reply_text(Translation.AFTER_SUCCESSFUL_UPLOAD_MSG, quote=True)
                
    else:
        await bot.send_message(
            chat_id=message.chat.id,
            text="You're B A N N E D",
            reply_to_message_id=message.message_id
        )

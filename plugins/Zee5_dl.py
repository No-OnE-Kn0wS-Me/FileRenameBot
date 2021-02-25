import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

import os
import re
import json
import math
import time
import shutil
import random
import ffmpeg
import asyncio
import requests

if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config

from translation import Translation
from database.database import *

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from datetime import datetime
from PIL import Image

from helper_funcs.display_progress import progress_for_pyrogram
from helper_funcs.display_progress import humanbytes
from helper_funcs.display_progress import headers
from helper_funcs.display_progress import take_screen_shot
from helper_funcs.display_progress import DownLoadFile



@Client.on_message(filters.private & filters.regex(pattern=".*http.*"))
async def zee5_capture(bot, update):

    if update.from_user.id in Config.BANNED_USERS:
        await bot.delete_messages(
            chat_id=update.chat.id,
            message_ids=update.message_id,
            revoke=True
        )
        return

    logger.info(update.from_user.id)
    
    if "zee5" in update.text:
        try:
            w = update.text 
            req1 = requests.get("https://useraction.zee5.com/tokennd").json()
            rgx = re.findall("([0-9]?\w+)", w)[-3:]
            li = { "url":"zee5vodnd.akamaized.net", "token":"https://gwapi.zee5.com/content/details/" }
            req2 = requests.get("https://useraction.zee5.com/token/platform_tokens.php?platform_name=web_app").json()["token"]
            headers["X-Access-Token"] = req2
            req3 = requests.get("https://useraction.zee5.com/token").json()    
            if "movies" in w:
                    r1 = requests.get(li["token"] + "-".join(rgx),
                                                headers=headers, 
                                                params={"translation":"en", "country":"IN"}).json()
                    g1 = (r1["hls"][0].replace("drm", "hls") + req1["video_token"])
                    file_name = r1["title"]
                    url = "https://" + li["url"] + g1
            elif "tvshows" or "originals" in w:
                    r2 = requests.get(li["token"] + "-".join(rgx), 
                                                headers=headers, 
                                                params={"translation":"en", "country":"IN"}).json()
                    g2 = (r2["hls"][0].replace("drm", "hls"))
                    if "netst" in g2:
                        file_name = r2["title"]
                        url = g2 + req3["video_token"]               
                    else:
                        file_name = r2["title"]
                        url = "https://" + li["url"] + g2 + req1["video_token"]
                    
            logger.info(url)
        except:
            await update.reply_text("There's some issue with your URL ", quote=True)
            return
            
    else:
        await update.reply_text("I can download from Zee5 links only! Use any url uploader for other links 😇", quote=True)
        return
    
    try:
        zee5_capture.url = url    
        
        command_to_exec = [
            "youtube-dl",
            "--no-warnings",
            "--youtube-skip-dash-manifest",
            "-j",
            url,
            "--geo-bypass-country",
            "IN"
        ]
        process = await asyncio.create_subprocess_exec(
            *command_to_exec,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        e_response = stderr.decode().strip()
        t_response = stdout.decode().strip()

        if e_response:
            logger.info(e_response)

        if t_response:
            x_reponse = t_response
            if "\n" in x_reponse:
                x_reponse, _ = x_reponse.split("\n")
            response_json = json.loads(x_reponse)
            save_ytdl_json_path = Config.DOWNLOAD_LOCATION + \
                "/" + str(update.from_user.id) + ".json"
            with open(save_ytdl_json_path, "w", encoding="utf8") as outfile:
                json.dump(response_json, outfile, ensure_ascii=False)
            inline_keyboard = []
            duration = None
            if "duration" in response_json:
                duration = response_json["duration"]
            if "formats" in response_json:
                for formats in response_json["formats"]:
                    format_id = formats.get("format_id")
                    format_string = formats.get("format_note")
                    if format_string is None:
                        format_string = formats.get("format")
                    format_ext = formats.get("ext")
                    approx_file_size = ""
                    if "filesize" in formats:
                        approx_file_size = humanbytes(formats["filesize"])
                    cb_string_video = "{}|{}|{}".format(
                        "video", format_id, format_ext)
                    cb_string_file = "{}|{}|{}".format(
                        "file", format_id, format_ext)
                    if format_string is not None and not "audio only" in format_string:
                        ikeyboard = [
                            InlineKeyboardButton(
                                "🎞 (" + format_string + ") " + approx_file_size + " ",
                                callback_data=(cb_string_video).encode("UTF-8")
                            ),
                            InlineKeyboardButton(
                                "📁 FILE " + format_ext + " " + approx_file_size + " ",
                                callback_data=(cb_string_file).encode("UTF-8")
                            )
                        ]                           
                        inline_keyboard.append(ikeyboard)
                        
            inline_keyboard.append([
                InlineKeyboardButton(
                    "✖️ CLOSE ✖️",
                     callback_data=(
                        "closeformat").encode("UTF-8")
                )
             ])

            reply_markup = InlineKeyboardMarkup(inline_keyboard)
            thumbnail = Config.DEF_THUMB_NAIL_VID_S
            thumbnail_image = Config.DEF_THUMB_NAIL_VID_S
            if "thumbnail" in response_json:
               if response_json["thumbnail"] is not None:
                   thumbnail = response_json["thumbnail"]
                   thumbnail_image = response_json["thumbnail"]
            thumb_image_path = DownLoadFile(
                thumbnail_image,
                Config.DOWNLOAD_LOCATION + "/" +
                str(update.from_user.id) + ".jpg",
                Config.CHUNK_SIZE,
                None,  # bot,
                Translation.DOWNLOAD_START,
                update.message_id,
                update.chat.id
            )   
 
            await bot.send_message(
                chat_id=update.chat.id,
                text=Translation.FORMAT_SELECTION.format(thumbnail),
                reply_markup=reply_markup,
                parse_mode="html",
                reply_to_message_id=update.message_id
            )
        else:
            await update.reply_text("There's some issue with your URL 😕 Or may be DRM protected!", quote=True)
            return
    except:
        await update.reply_text("Couldn't download your video!", quote=True)
        logger.info('format send error')
        return
             
async def zee5_execute(bot, update):
  
    try:
        cb_data = update.data
        tg_send_type, youtube_dl_format, youtube_dl_ext = cb_data.split("|")
        
        thumb_image_path = Config.DOWNLOAD_LOCATION + \
            "/" + str(update.from_user.id) + ".jpg"

        save_ytdl_json_path = Config.DOWNLOAD_LOCATION + \
            "/" + str(update.from_user.id) + ".json"
        try:
            with open(save_ytdl_json_path, "r", encoding="utf8") as f:
                response_json = json.load(f)
        except (FileNotFoundError) as e:
            await bot.delete_messages(
                chat_id=update.message.chat.id,
                message_ids=update.message.message_id,
                revoke=True
            )
            return False
        
        youtube_dl_url = zee5_capture.url
        
        linksplit = update.message.reply_to_message.text.split("/")
        videoname = linksplit[+5]
        logger.info(videoname)
        
        custom_file_name = videoname + ".mp4"

        await bot.edit_message_text(
            text=Translation.DOWNLOAD_START,
            chat_id=update.message.chat.id,
            message_id=update.message.message_id
        )
        description = Translation.CUSTOM_CAPTION_UL_FILE.format(newname=custom_file_name)

        tmp_directory_for_each_user = Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id)
        if not os.path.isdir(tmp_directory_for_each_user):
            os.makedirs(tmp_directory_for_each_user)
        download_directory = tmp_directory_for_each_user + "/" + custom_file_name
        command_to_exec = []
        
        minus_f_format = youtube_dl_format + "+bestaudio"
        command_to_exec = [
            "youtube-dl",
            "-c",
            "--max-filesize", str(Config.TG_MAX_FILE_SIZE),
            "-f", minus_f_format,
            "--hls-prefer-ffmpeg", youtube_dl_url,
            "-o", download_directory
        ]                  
        command_to_exec.append("--no-warnings")
        command_to_exec.append("--geo-bypass-country")
        command_to_exec.append("IN")
        
        start = datetime.now()
        process = await asyncio.create_subprocess_exec(
            *command_to_exec,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        e_response = stderr.decode().strip()
        t_response = stdout.decode().strip()

        if os.path.isfile(download_directory):
            logger.info("no issues")
        else:
            logger.info("issues found, passing to sub process")
            command_to_exec.clear()
            minus_f_format = youtube_dl_format
            command_to_exec = [
                "youtube-dl",
                "-c",
                "--max-filesize", str(Config.TG_MAX_FILE_SIZE),
                "-f", minus_f_format,
                "--hls-prefer-ffmpeg", youtube_dl_url,
                "-o", download_directory
            ]                  
            command_to_exec.append("--no-warnings")
            command_to_exec.append("--geo-bypass-country")
            command_to_exec.append("IN")
        
            start = datetime.now()
            process = await asyncio.create_subprocess_exec(
                *command_to_exec,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()
            e_response = stderr.decode().strip()
            t_response = stdout.decode().strip()

        ad_string_to_replace = "please report this issue on https://yt-dl.org/bug . Make sure you are using the latest version; see  https://yt-dl.org/update  on how to update. Be sure to call youtube-dl with the --verbose flag and include its complete output."
        if e_response and ad_string_to_replace in e_response:
            error_message = e_response.replace(ad_string_to_replace, "")
            await bot.edit_message_text(
                chat_id=update.message.chat.id,
                message_id=update.message.message_id,
                text=error_message
            )
            return False
        if t_response:
            os.remove(save_ytdl_json_path)
            end_one = datetime.now()
            time_taken_for_download = (end_one -start).seconds
            file_size = Config.TG_MAX_FILE_SIZE + 1
            try:
                file_size = os.stat(download_directory).st_size
            except FileNotFoundError as exc:
                download_directory = os.path.splitext(download_directory)[0] + "." + "mp4"
                file_size = os.stat(download_directory).st_size
            if file_size > Config.TG_MAX_FILE_SIZE:
                await bot.edit_message_text(
                    chat_id=update.message.chat.id,
                    text=Translation.RCHD_TG_API_LIMIT.format(time_taken_for_download, humanbytes(file_size)),
                    message_id=update.message.message_id
                )
            else:
                await bot.edit_message_text(
                    text=Translation.UPLOAD_START,
                    chat_id=update.message.chat.id,
                    message_id=update.message.message_id
                )

                # get the correct width, height, and duration for videos greater than 10MB
                width = 0
                height = 0
                duration = 0
                if tg_send_type != "file":
                    metadata = extractMetadata(createParser(download_directory))
                    if metadata is not None:
                        if metadata.has("duration"):
                            duration = metadata.get('duration').seconds            
                # get the correct width, height, and duration for videos greater than 10MB
                
                if not os.path.exists(thumb_image_path):
                    mes = await thumb(update.from_user.id)
                    if mes != None:
                        m = await bot.get_messages(update.chat.id, mes.msg_id)
                        await m.download(file_name=thumb_image_path)
                        thumb_image_path = thumb_image_path
                    else:
                        try:
                            thumb_image_path = await take_screen_shot(
                                download_directory,
                                os.path.dirname(download_directory),
                                random.randint(
                                    0,
                                    duration - 1
                                )
                            )
                        except:
                            thumb_image_path = None
                            pass  
                else:
                    width = 0
                    height = 0
                    metadata = extractMetadata(createParser(thumb_image_path))
                    if metadata.has("width"):
                        width = metadata.get("width")
                    if metadata.has("height"):
                        height = metadata.get("height")
                    if tg_send_type == "vm":
                        height = width               
                    Image.open(thumb_image_path).convert(
                        "RGB").save(thumb_image_path)
                    img = Image.open(thumb_image_path)
                    img.thumbnail((90, 90))
                    if tg_send_type == "file":
                        img.resize((320, height))
                    else:
                        img.resize((90, height))
                    img.save(thumb_image_path, "JPEG")
  
                start_time = time.time()

                if tg_send_type == "file":
                    await bot.send_document(
                        chat_id=update.message.chat.id,
                        document=download_directory,
                        thumb=thumb_image_path,
                        caption=description,
                        parse_mode="HTML",
                        # reply_markup=reply_markup,
                        reply_to_message_id=update.message.reply_to_message.message_id,
                        progress=progress_for_pyrogram,
                        progress_args=(
                            Translation.UPLOAD_START,
                            update.message,
                            start_time
                        )
                    )
                elif tg_send_type == "video":
                    await bot.send_video(
                        chat_id=update.message.chat.id,
                        video=download_directory,
                        caption=description,
                        parse_mode="HTML",
                        duration=duration,
                        width=width,
                        height=height,
                        supports_streaming=True,
                        # reply_markup=reply_markup,
                        thumb=thumb_image_path,
                        reply_to_message_id=update.message.reply_to_message.message_id,
                        progress=progress_for_pyrogram,
                        progress_args=(
                            Translation.UPLOAD_START,
                            update.message,
                            start_time
                        )
                    )
                else:
                    logger.info("Did this happen? :\\")

                try:
                    shutil.rmtree(tmp_directory_for_each_user)
                except:
                    pass
                try:
                    os.remove(thumb_image_path)
                except:
                    pass

                await bot.edit_message_text(
                    text=Translation.AFTER_SUCCESSFUL_UPLOAD_MSG_WITH_TS,
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="Support Channel", url="https://t.me/Mai_bOTs")]]),
                    chat_id=update.message.chat.id,
                    message_id=update.message.message_id,
                    disable_web_page_preview=True
                )               
    except:
        await update.reply_text("Couldn't download your video!", quote=True)
        logger.info('error in process') 

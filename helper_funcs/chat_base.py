#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K

import os

# the secret configuration specific things
if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config

# the Strings used for this "thing"
from translation import Translation

from pyrogram import Client, Filters

# the Telegram trackings
from chatbase import Message


def TRChatBase(chat_id, message_text, intent):
    msg = Message(api_key=Config.CHAT_BASE_TOKEN,
              platform="Telegram",
              version="1.3",
              user_id=chat_id,
              message=message_text,
              intent=intent)
    resp = msg.send()

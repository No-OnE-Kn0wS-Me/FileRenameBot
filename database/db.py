from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

import os

import threading
import asyncio

from sqlalchemy import Column, Integer, Boolean, String, ForeignKey, UniqueConstraint, func


from sample_config import Config


def start() -> scoped_session:
    engine = create_engine(Config.DB_URI, client_encoding="utf8")
    BASE.metadata.bind = engine
    BASE.metadata.create_all(engine)
    return scoped_session(sessionmaker(bind=engine, autoflush=False))


BASE = declarative_base()
SESSION = start()

INSERTION_LOCK = threading.RLock()

class custom_caption(BASE):
    __tablename__ = "caption"
    id = Column(Integer, primary_key=True)
    caption = Column(String)
    
    def __init__(self, id, caption):
        self.id = id
        self.caption = caption

custom_caption.__table__.create(checkfirst=True)

async def update_cap(id, caption):
    with INSERTION_LOCK:
        cap = SESSION.query(custom_caption).get(id)
        if not cap:
            cap = custom_caption(id, caption)
            SESSION.add(cap)
            SESSION.flush()
        else:
            SESSION.delete(cap)
            cap = custom_caption(id, caption)
            SESSION.add(cap)
        SESSION.commit()

async def del_caption(id):
    with INSERTION_LOCK:
        msg = SESSION.query(custom_caption).get(id)
        SESSION.delete(msg)
        SESSION.commit()

async def get_caption(id):
    try:
        caption = SESSION.query(custom_caption).get(id)
        return caption
    finally:
        SESSION.close()

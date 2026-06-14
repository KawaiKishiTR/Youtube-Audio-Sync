
from dataclasses import dataclass
from typing import Any, Callable, Generator, Optional

from app.database import SessionLocal, Playlist
from app.data_manager import DataManager
from app.object_class import yt_playlist, yt_video


@dataclass
class flow_context:
    data_manager:DataManager
    playlist: Optional[yt_playlist]
    media: Optional[yt_video]

def main_flow():
    db = SessionLocal()
    ctx = flow_context(DataManager(db), None, None)
    pl_data = db.query(Playlist).all()
    for pl in pl_data:
        ctx.playlist = yt_playlist(pl.playlist_yt_id)
        ctx.media = None
        single_playlist_flow(ctx)

def single_playlist_flow(ctx:flow_context):
    for media in ctx.playlist.info.entries:
        ctx.media = media
        single_media_flow(ctx)

def single_media_flow(ctx:flow_context):
    path = ctx.media.download()
    ctx.data_manager.upsert_media(ctx.media, path)
    ctx.data_manager.link_media_to_playlist(
        ctx.data_manager.get_media(ctx.media),
        ctx.data_manager.get_or_create_playlist(ctx.playlist)
    )


def try_that(func:Callable, ctx:flow_context, *args, **kwargs) -> Any:
    try:
        func(*args, **kwargs)
    except Exception as e:
        print(f"HATA: {e}")
        print(f"PAYLOAD: PL:{ctx.playlist.id} and VD:{ctx.media.id}")



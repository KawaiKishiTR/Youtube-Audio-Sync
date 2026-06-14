from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from app.database import SessionLocal, Playlist
from app.data_manager import DataManager
from app.object_class import yt_playlist, yt_video

@dataclass
class flow_context:
    data_manager: DataManager
    playlist: Optional[yt_playlist]
    media: Optional[yt_video]

def main_flow():
    print("[MAIN] Ana akış (Main flow) başlatılıyor...")
    db = SessionLocal()
    ctx = flow_context(DataManager(db), None, None)
    
    pl_data = db.query(Playlist).all()
    print(f"[MAIN] Veritabanında (Database) toplam {len(pl_data)} adet playlist bulundu.")
    
    for index, pl in enumerate(pl_data, start=1):
        print(f"\n==================================================")
        print(f"[PLAYLIST] ({index}/{len(pl_data)}) ID: '{pl.playlist_yt_id}' işleniyor...")
        
        ctx.playlist = yt_playlist(pl.playlist_yt_id)
        ctx.media = None
        single_playlist_flow(ctx)
        
        print(f"[PLAYLIST] ID: '{pl.playlist_yt_id}' için tüm işlemler tamamlandı.")
        
    print("\n[MAIN] Tüm playlist akışları başarıyla sonlandı.")

def single_playlist_flow(ctx: flow_context):
    print(f"  -> [INFO] Playlist meta verileri (Metadata) çekiliyor...")
    
    # ctx.playlist.info.entries çağrıldığında subprocess çalışacak, bu yüzden öncesinde log veriyoruz
    for media in ctx.playlist.info.entries:
        media_data = ctx.data_manager.get_media(media)
        if media_data and not Path(media_data.file_path).exists():
            print(f"    -> [SKIP] Medya ({media.id}) veritabanında bulundu. Atlanıyor.")
            continue
            
        print(f"    -> [NEW] Medya ({media.id}) bulunamadı. Akışa (Flow) dahil ediliyor...")
        ctx.media = media
        single_media_flow(ctx)

def single_media_flow(ctx: flow_context):
    print(f"      * [DOWNLOAD] Subprocess başlatılıyor: {ctx.media.id} ...")
    path = ctx.media.download()
    print(f"      * [DOWNLOAD] Başarılı. Kaydedilen yol (Path): {path}")
    
    ctx.data_manager.upsert_media(ctx.media, path)
    
    ctx.data_manager.link_media_to_playlist(
        ctx.data_manager.get_media(ctx.media),
        ctx.data_manager.get_or_create_playlist(ctx.playlist)
    )
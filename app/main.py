
from app.process_flow import main_flow
from app.database import SessionLocal, init_db
from app.data_manager import DataManager
from app.object_class import yt_playlist
import argparse

def main():
    init_db()
    parser = argparse.ArgumentParser(description="YouTube Playlist Senkronizasyon Aracı")
    
    # Alt ayrıştırıcıları (Subparsers) oluştur
    subparsers = parser.add_subparsers(dest="command", required=True, help="Kullanılabilir komutlar (Available commands)")
    
    # process komutu
    subparsers.add_parser("process", help="Veritabanındaki tüm playlistleri tarar ve eksikleri indirir")
    
    # addlist komutu
    add_parser = subparsers.add_parser("addlist", help="Sisteme yeni bir playlist ekler")
    add_parser.add_argument("playlist_id", type=str, help="YouTube Playlist ID'si (örn: PL_abcdef...)")
    
    # removelist komutu
    remove_parser = subparsers.add_parser("removelist", help="Sistemden bir playlisti siler")
    remove_parser.add_argument("playlist_id", type=str, help="Silinecek YouTube Playlist ID'si")
    
    # Terminalden gelen argümanları ayrıştır
    args = parser.parse_args()
    
    if args.command == "process":
        main_flow()
    elif args.command == "addlist":
        DataManager(SessionLocal()).get_or_create_playlist(yt_playlist(args.playlist_id))
    elif args.command == "removelist":
        raise NotImplementedError




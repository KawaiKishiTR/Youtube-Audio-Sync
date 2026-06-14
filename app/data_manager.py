from sqlalchemy.orm import Session
from app.database import Media, Playlist
from app.object_class import yt_video, yt_playlist

class DataManager:
    def __init__(self, session: Session):
        """Sınıf başlatılırken aktif bir veritabanı oturumu (Database Session) alır."""
        self.session = session

    def get_or_create_playlist(self, p_id: yt_playlist) -> Playlist:
        """
        Playlist wrapper objesini alır, veritabanında arar.
        Yoksa yeni bir kayıt oluşturup döner (Get or Create).
        """
        db_playlist = self.session.query(Playlist).filter_by(playlist_yt_id=p_id.id).first()
        
        if not db_playlist:
            db_playlist = Playlist(playlist_yt_id=p_id.id)
            self.session.add(db_playlist)
            self.session.commit()
            self.session.refresh(db_playlist)
            
        return db_playlist

    def get_media(self, y_id: yt_video) -> Media | None:
        """
        yt_id wrapper objesini kullanarak medya kaydını çeker.
        Bulamazsa None döner.
        """
        return self.session.query(Media).filter_by(youtube_id=y_id.id).first()

    def upsert_media(self, y_id: yt_video, file_path: str) -> Media:
        """
        Medya veritabanında yoksa ekler (Insert), varsa dosya yolunu günceller (Update).
        Bu iki işlemin birleşimine 'Upsert' (Update or Insert) denir.
        """
        db_media = self.get_media(y_id)
        
        if not db_media:
            db_media = Media(youtube_id=y_id.id, file_path=file_path)
            self.session.add(db_media)
        else:
            # Dosya silinip tekrar indirilmişse veya konumu değişmişse yolu güncelleriz
            db_media.file_path = file_path
            
        self.session.commit()
        self.session.refresh(db_media)
        return db_media

    def link_media_to_playlist(self, db_media: Media, db_playlist: Playlist):
        """
        Bir Media kaydını bir Playlist kaydına bağlar.
        Eğer ilişki (Relationship) zaten varsa işlem yapmaz.
        """
        if db_playlist not in db_media.playlists:
            db_media.playlists.append(db_playlist)
            self.session.commit()

from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

# Many-to-Many İlişki Tablosu
media_playlist_association = Table(
    'media_playlist',
    Base.metadata,
    Column('media_id', Integer, ForeignKey('media.id', ondelete="CASCADE"), primary_key=True),
    Column('playlist_id', Integer, ForeignKey('playlists.id', ondelete="CASCADE"), primary_key=True)
)

class Media(Base):
    __tablename__ = 'media'
    id = Column(Integer, primary_key=True)
    youtube_id = Column(String, unique=True, nullable=False, index=True)
    file_path = Column(String, nullable=False)
    
    playlists = relationship(
        "Playlist",
        secondary=media_playlist_association,
        back_populates="medias"
    )

class Playlist(Base):
    __tablename__ = 'playlists'
    id = Column(Integer, primary_key=True)
    playlist_yt_id = Column(String, unique=True, nullable=False, index=True)
    
    medias = relationship(
        "Media",
        secondary=media_playlist_association,
        back_populates="playlists"
    )
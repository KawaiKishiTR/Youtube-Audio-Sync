import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .tables import Base

# Veritabanı dosyasını dinamik olarak app/data/ altına konumlandırıyoruz
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(DB_DIR, exist_ok=True)
DATABASE_URL = f"sqlite:///{os.path.join(DB_DIR, 'media_library.db')}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
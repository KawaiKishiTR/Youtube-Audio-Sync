

import json
import os
import yt_dlp
from pathlib import Path
from copy import deepcopy

from app.function_utils import type_check_raise, sanitize_string

DOWNLOAD_PATH = Path(os.environ["DOWNLOAD_PATH"])
DOWNLOAD_PATH.mkdir(exist_ok=True, parents=True)

class yt_video:
    _download_opts = {
        'format': 'bestaudio/best',
        'remote_components': ['ejs:github'],
        'writethumbnail': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        },
        {
            'key': 'FFmpegMetadata',  # Şarkı adı, sanatçı gibi meta verileri (Metadata) gömer
        },
        {
            'key': 'EmbedThumbnail',  # Kapak fotoğrafını MP3 dosyasına gömer ve geçici resim dosyasını siler
        }],
        'quiet': True,
    }

    info_opts = {
        'remote_components': ['ejs:github'],
        'quiet': True,
        'skip_download': True
    }

    def __init__(self, yt_id:str):
        type_check_raise(yt_id, str)
        self.id = yt_id
        self.url = f"https://www.youtube.com/watch?v={self.id}"

        self.__info = None

    @property
    def info(self):
        if not self.__info:
            with yt_dlp.YoutubeDL(self.info_opts) as ydl:
                meta = ydl.extract_info(self.url, download=False)
            self.__info = video_info(meta)
        return self.__info

    @property
    def download_opts(self):
        opts = deepcopy(self._download_opts)
        opts["outtmpl"] = f"{str(DOWNLOAD_PATH / self.info.path_string)}.%(ext)s"
        return opts

    def download(self):
        with yt_dlp.YoutubeDL(self.download_opts) as ydl:
            info_dict = ydl.extract_info(self.url, download=True)
            prepared_file_name = ydl.prepare_filename(info_dict)
            return str(Path(prepared_file_name).with_suffix(".mp3"))

class video_info:
    def __init__(self, infodict):
        self.infodict = infodict
    
    @property
    def artist(self) -> str:
        getters = [
            lambda:self.infodict.get("artist", None),
            lambda:self.infodict.get("uploader", None),
            lambda:"UnknownArtist"
        ]
        for getter in getters:
            value = getter()
            if value:
                return sanitize_string(value)
            
    @property
    def album(self) -> str:
        return sanitize_string(self.infodict.get("album", "UnknownAlbum"))

    @property
    def title(self) -> str:
        return sanitize_string(self.infodict.get("title", "UnknownTitle"))

    @property
    def path_string(self) -> str:
        return f"{self.artist}/{self.album}/{self.title}"

class playlist_info:
    def __init__(self, infodict):
        self.infodict = infodict

    @property
    def id(self) -> str:
        """Playlist'in benzersiz kimliği (Unique Identifier)."""
        return self.infodict.get("id", "UnknownPlaylistID")

    @property
    def title(self) -> str:
        """Playlist'in başlığı."""
        return sanitize_string(self.infodict.get("title", "UnknownPlaylist"))

    @property
    def uploader(self) -> str:
        """Playlist'i oluşturan kanal veya kullanıcı."""
        return sanitize_string(self.infodict.get("uploader", "UnknownUploader"))
    
    @property
    def entries(self):
        """
        Playlist içindeki videoların ID'lerini bir üreteç (Generator) olarak döner.
        Böylece bellek (Memory) şişirilmeden videolar sırayla işlenebilir.
        """
        # extract_flat kullanıldığı için entries listesindeki objeler sadece temel bilgileri içerir.
        entries_list = self.infodict.get("entries", [])
        
        for entry in entries_list:
            if not entry:
                continue
            id_ = entry.get("id", None)
            if not id_:
                continue
            yield yt_video(id_)

class yt_playlist:
    info_opts = {
        'remote_components': ['ejs:github'],
        'extract_flat': 'in_playlist',
        'quiet': True
    }


    def __init__(self, pl_id:str):
        type_check_raise(pl_id, str)
        self.id = pl_id
        self.url = f"https://www.youtube.com/watch?list={self.id}"

        self.__info = None
    
    @property
    def info(self) -> playlist_info:
        if not self.__info:
            with yt_dlp.YoutubeDL(self.info_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)
                self.__info = playlist_info(info)
        return self.__info
    

JS_RUNTIME = os.environ.get("JS_RUNTIME", None)
if JS_RUNTIME is not None and Path(JS_RUNTIME).exists():
    runtime_dict = {'node':{'path':str(Path(JS_RUNTIME))}, 'deno':{'path':None}}
    yt_video.info_opts["js_runtimes"] = runtime_dict
    yt_video._download_opts["js_runtimes"] = runtime_dict
    yt_playlist.info_opts["js_runtimes"] = runtime_dict

FFMPEG_LOCATION = os.environ.get("FFMPEG_LOCATION", None)
if FFMPEG_LOCATION is not None and Path(FFMPEG_LOCATION).exists():
    yt_video._download_opts['ffmpeg_location'] = str(Path(FFMPEG_LOCATION))

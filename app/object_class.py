

import os
from pathlib import Path

from app.function_utils import type_check_raise, sanitize_string, run_process

DOWNLOAD_PATH = Path(os.environ["DOWNLOAD_PATH"])
DOWNLOAD_PATH.mkdir(exist_ok=True, parents=True)

### ----- INSTRUCTING COMMON ARGS -----
YT_DLP = os.environ.get("YT_DLP_LOCATION")
if YT_DLP is None or not Path(YT_DLP).exists():
    YT_DLP = "yt-dlp"

COMMON_ARGS = [YT_DLP, "--remote-components", "ejs:github", "--quiet"]

JS_RUNTIME = os.environ.get("JS_RUNTIME", None)
if JS_RUNTIME is not None and Path(JS_RUNTIME).exists():
    COMMON_ARGS.extend(["--js-runtimes", f"node:{JS_RUNTIME}"])
else:
    COMMON_ARGS.extend(["--js-runtimes", "node"])    

FFMPEG_LOCATION = os.environ.get("FFMPEG_LOCATION", None)
if FFMPEG_LOCATION is not None and Path(FFMPEG_LOCATION).exists():
    COMMON_ARGS.extend(["--ffmpeg-location", FFMPEG_LOCATION])
### ------------------------------------------

class yt_video:
    download_opts = [
        *COMMON_ARGS,
        "--format", "bestaudio/best",
        "--extract-audio",
        "--audio-format", "mp3",
        "--audio-quality", "192",
        "--add-metadata",
        "--embed-thumbnail",
    ]

    info_opts = [
        *COMMON_ARGS,
        "--skip-download",
        "--dump-json"
    ]

    def __init__(self, yt_id:str):
        type_check_raise(yt_id, str)
        self.id = yt_id
        self.url = f"https://www.youtube.com/watch?v={self.id}"

        self.__info = None

    @property
    def info(self):
        if not self.__info:
            self.__info = video_info(run_process([*self.info_opts, self.url], return_json=True))
        return self.__info

    def download(self):
        base_path = DOWNLOAD_PATH / self.info.path_string
        base_path.parent.mkdir(exist_ok=True, parents=True)

        opts = [
            *self.download_opts,
            "--output", f"{str(base_path)}.%(ext)s",
            self.url
        ]

        run_process(opts)
        return str(base_path.with_suffix(".mp3"))

class video_info:
    def __init__(self, infodict):
        self.infodict = infodict
    
    @property
    def artist(self) -> str:
        # Ana sanatçıyı ayıklama ve temizleme fonksiyonu (Primary Artist Extraction)
        def extract_primary_artist(text: str) -> str | None:
            if not text:
                return None
            
            # 1. Ayırıcılardan (Delimiters) böl ve sadece ilkini al
            delimiters = [",", "&", " feat.", " ft.", " x "]
            for delimiter in delimiters:
                if delimiter in text:
                    text = text.split(delimiter)[0]
            
            # 2. İstenmeyen kanal eklerini (Suffixes) temizle
            text = text.replace(" - Topic", "").replace("VEVO", "")
            
            # 3. Kalan dizeyi temizle (Sanitize) ve boşlukları kırp (Trim)
            cleaned = sanitize_string(text.strip())
            return cleaned if cleaned else None

        # 1. Öncelik: Platformun verdiği 'artist' verisi
        raw_artist = self.infodict.get("artist")
        primary_artist = extract_primary_artist(raw_artist)
        if primary_artist:
            return primary_artist
            
        # 2. Öncelik: Yükleyici (Uploader) kanal adı
        raw_uploader = self.infodict.get("uploader")
        primary_uploader = extract_primary_artist(raw_uploader)
        if primary_uploader:
            return primary_uploader
            
        # 3. Öncelik: Fallback (Varsayılan değer)
        return "UnknownArtist"

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
    info_opts = [
        *COMMON_ARGS,
        "--flat-playlist",
        "--dump-single-json",
    ]

    def __init__(self, pl_id:str):
        type_check_raise(pl_id, str)
        self.id = pl_id
        self.url = f"https://www.youtube.com/watch?list={self.id}"

        self.__info = None
    
    @property
    def info(self) -> playlist_info: #TODO: subprocess
        if not self.__info:
            self.__info = playlist_info(run_process([*self.info_opts, self.url], return_json=True))
        return self.__info


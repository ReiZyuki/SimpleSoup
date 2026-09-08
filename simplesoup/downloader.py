import os
import urllib.request
import yt_dlp

from .parser import STAGES


class Downloader:

    def __init__(self):
        self.path = "/storage/emulated/0/Download/ReiDownloader"
        os.makedirs(self.path, exist_ok=True)

    # ============================================================
    # Helpers
    # ============================================================

    def _format_speed(self, speed):
        if not speed:
            return "0 KB/s"

        if speed >= 1024 * 1024:
            return f"{speed / (1024 * 1024):.1f} MB/s"

        return f"{speed / 1024:.0f} KB/s"

    def _progress_hook(
        self,
        data,
        mode="Video",
        progress_callback=None
    ):

        status = data.get("status")

        if status == "downloading":

            total = (
                data.get("total_bytes")
                or data.get("total_bytes_estimate")
            )

            downloaded = data.get("downloaded_bytes", 0)
            speed = data.get("speed")

            if total:
                percent = (downloaded / total) * 100
            else:
                percent = 0

            network = self._format_speed(speed)

            print(
                f"\r[Download {percent:.0f}%] "
                f"[Network {network}] "
                f"[Mode {mode}]",
                end="",
                flush=True
            )

            if progress_callback:
                try:
                    progress_callback(
                        f"{percent:.0f}%",
                        network,
                        mode
                    )
                except Exception:
                    pass

        elif status == "finished":

            network = self._format_speed(
                data.get("speed")
            )

            print(
                f"\r[Download 100%] "
                f"[Network {network}] "
                f"[Mode {mode}]"
            )

            if progress_callback:
                try:
                    progress_callback(
                        "100%",
                        network,
                        mode
                    )
                except Exception:
                    pass

    def _get_format(self, quality):

        if quality == "audio":

            return (
                "bestaudio[acodec^=mp4a]/"
                "bestaudio"
            )

        elif quality == "best":

            return (
                "bestvideo[vcodec^=avc1]+"
                "bestaudio[acodec^=mp4a]/"
                "bestvideo[vcodec^=avc1]+"
                "bestaudio/"
                "best"
            )

        else:

            height = quality.replace("p", "")

            return (
                f"bestvideo[height<={height}]"
                f"[vcodec^=avc1]+"
                f"bestaudio[acodec^=mp4a]/"
                f"bestvideo[height<={height}]"
                f"[vcodec^=avc1]+"
                f"bestaudio/"
                f"best"
            )

    # ============================================================
    # Main Engine
    # ============================================================

    def cookie_exists(self, cookie):
        return os.path.isfile(cookie)

    def test_cookie(self, url, cookie):
        options = {
            "quiet": True,
            "no_warnings": True,
            "cookiefile": cookie
        }

        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.extract_info(
                url,
                download=False
            )

    def execute(
        self,
        config,
        cookies=None,
        progress_callback=None
    ):

        url = config["url"]

        # ---------------------------------
        # Cookie validation
        # ---------------------------------

        if cookies:

            if not os.path.isfile(cookies):
                raise FileNotFoundError(
                    f"Cookies file not found: {cookies}"
                )

        # ---------------------------------
        # Find playlist block
        # ---------------------------------

        playlist = None

        for block in config["blocks"]:

            if block["type"] == "playlist":
                playlist = block
                break

        # ---------------------------------
        # Find video block
        # ---------------------------------

        video = None

        for block in config["blocks"]:

            if block["type"] == "video":
                video = block
                break

        # =========================================================
        # PLAYLIST ENGINE
        # =========================================================

        if playlist is not None:

            quality_stage = playlist["quality"]
            skip = playlist["skip"]
            count = playlist["count"]

            quality = STAGES[quality_stage]

            fmt = self._get_format(quality)

            # -----------------------------------------------------
            # Metadata + playlist title
            # -----------------------------------------------------

            metadata_options = {
                "quiet": True,
                "no_warnings": True,
                "extract_flat": True,
                "noplaylist": False
            }

            if cookies:
                metadata_options["cookiefile"] = cookies

            with yt_dlp.YoutubeDL(
                metadata_options
            ) as ydl:

                playlist_info = ydl.extract_info(
                    url,
                    download=False
                )

            result = {}

            # -----------------------------------------------------
            # Metadata blocks
            # -----------------------------------------------------

            for block in config["blocks"]:

                variable = block["variable"]

                if not variable:
                    continue

                block_type = block["type"]

                if block_type == "title":

                    result[variable] = playlist_info.get(
                        "title"
                    )

                elif block_type == "creator":

                    result[variable] = (
                        playlist_info.get("uploader")
                        or playlist_info.get("channel")
                    )

                elif block_type == "url":

                    result[variable] = (
                        playlist_info.get("webpage_url")
                        or url
                    )

                elif block_type == "views":

                    result[variable] = playlist_info.get(
                        "view_count"
                    )

                elif block_type == "likes":

                    result[variable] = playlist_info.get(
                        "like_count"
                    )

                elif block_type == "count":

                    result[variable] = playlist_info.get(
                        "comment_count"
                    )

                elif block_type == "time":

                    result[variable] = playlist_info.get(
                        "duration"
                    )

                elif block_type == "playlist_title":

                    result[variable] = playlist_info.get(
                        "title"
                    )

            # -----------------------------------------------------
            # Playlist range
            # -----------------------------------------------------

            start = skip + 1
            end = skip + count

            playlist_items = f"{start}-{end}"

            output = os.path.join(
                self.path,
                "%(title)s.%(ext)s"
            )

            options = {
                "format": fmt,
                "outtmpl": output,
                "noplaylist": False,
                "playlist_items": playlist_items,
                "merge_output_format": "mp4",
                "quiet": True,
                "no_warnings": True,
                "progress_hooks": [
                    lambda data: self._progress_hook(
                        data,
                        "Playlist",
                        progress_callback
                    )
                ]
            }

            if cookies:
                options["cookiefile"] = cookies

            print(
                f"Playlist download: "
                f"quality={quality}, "
                f"skip={skip}, "
                f"count={count}"
            )

            # -----------------------------------------------------
            # Download playlist
            # -----------------------------------------------------

            downloaded_files = []

            with yt_dlp.YoutubeDL(options) as ydl:

                final_info = ydl.extract_info(
                    url,
                    download=True
                )

                entries = final_info.get(
                    "entries",
                    []
                )

                for entry in entries:

                    if not entry:
                        continue

                    filepath = ydl.prepare_filename(
                        entry
                    )

                    if not os.path.exists(filepath):

                        mp4_path = (
                            os.path.splitext(filepath)[0]
                            + ".mp4"
                        )

                        if os.path.exists(mp4_path):
                            filepath = mp4_path

                    if os.path.exists(filepath):

                        downloaded_files.append(
                            filepath
                        )

            # -----------------------------------------------------
            # Return playlist files
            # -----------------------------------------------------

            result["videos"] = downloaded_files

            return result

        # =========================================================
        # NORMAL SINGLE-VIDEO ENGINE
        # =========================================================

        metadata_options = {
            "quiet": True,
            "no_warnings": True
        }

        if cookies:
            metadata_options["cookiefile"] = cookies

        with yt_dlp.YoutubeDL(
            metadata_options
        ) as ydl:

            info = ydl.extract_info(
                url,
                download=False
            )

        result = {}

        # ---------------------------------
        # Metadata blocks
        # ---------------------------------

        for block in config["blocks"]:

            variable = block["variable"]

            if not variable:
                continue

            block_type = block["type"]

            if block_type == "title":

                result[variable] = info.get(
                    "title"
                )

            elif block_type == "creator":

                result[variable] = (
                    info.get("uploader")
                    or info.get("channel")
                )

            elif block_type == "url":

                result[variable] = (
                    info.get("webpage_url")
                    or url
                )

            elif block_type == "views":

                result[variable] = info.get(
                    "view_count"
                )

            elif block_type == "likes":

                result[variable] = info.get(
                    "like_count"
                )

            elif block_type == "count":

                result[variable] = info.get(
                    "comment_count"
                )

            elif block_type == "time":

                result[variable] = info.get(
                    "duration"
                )

            elif block_type == "thumbnail":

                thumbnail_url = info.get(
                    "thumbnail"
                )

                if thumbnail_url:

                    title = (
                        info.get("title")
                        or "thumbnail"
                    )

                    thumbnail_path = os.path.join(
                        self.path,
                        f"{title}.jpg"
                    )

                    urllib.request.urlretrieve(
                        thumbnail_url,
                        thumbnail_path
                    )

                    result[variable] = thumbnail_path

                else:

                    result[variable] = None

            elif block_type == "formats":

                result[variable] = info.get(
                    "formats",
                    []
                )

        # ---------------------------------
        # Metadata-only request
        # ---------------------------------

        if video is None:
            return result

        # ---------------------------------
        # Quality
        # ---------------------------------

        stage = video["stage"]

        quality = STAGES[stage]

        fmt = self._get_format(quality)

        # ---------------------------------
        # Download options
        # ---------------------------------

        output = os.path.join(
            self.path,
            "%(title)s.%(ext)s"
        )

        options = {
            "format": fmt,
            "outtmpl": output,
            "noplaylist": True,
            "merge_output_format": "mp4",
            "quiet": True,
            "progress_hooks": [
                lambda data: self._progress_hook(
                    data,
                    "Video",
                    progress_callback
                )
            ]
        }

        if cookies:
            options["cookiefile"] = cookies

        print(
            f"Downloading: {quality}"
        )

        with yt_dlp.YoutubeDL(options) as ydl:

            final_info = ydl.extract_info(
                url,
                download=True
            )

            filepath = ydl.prepare_filename(
                final_info
            )

        if not os.path.exists(filepath):

            mp4_path = (
                os.path.splitext(filepath)[0]
                + ".mp4"
            )

            if os.path.exists(mp4_path):
                filepath = mp4_path

        result[video["variable"]] = filepath

        return result

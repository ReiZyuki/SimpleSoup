from .parser import parse
from .downloader import Downloader
from .gallery import Gallery


# ============================================================
# SimpleSoup Configuration
# ============================================================

# Put your cookies.txt file path here.
# Example:
# COOKIES = "/storage/emulated/0/Download/instagram_cookies.txt"
#
# Disable cookies:
# COOKIES = None

COOKIES = "/storage/emulated/0/Download/reddit_cookies.txt"


class SimpleSoup:

    def __init__(self):
        self.downloader = Downloader()
        self.gallery = Gallery()

    def __call__(
        self,
        expression,
        url=None,
        progress_callback=None
    ):
        return self.run(
            expression,
            url,
            progress_callback
        )

    def run(
        self,
        expression,
        url=None,
        progress_callback=None
    ):

        config = parse(expression)

        if url is not None:
            config["url"] = url

        if not config["url"]:
            raise ValueError("URL missing")

        # ========================================================
        # Gallery-dl engine
        # ========================================================

        for block in config["blocks"]:

            if block["type"] == "gallery":

                result = self.gallery.execute(
                    config["url"],
                    cookies=COOKIES
                )

                if block["variable"]:

                    return {
                        block["variable"]: result
                    }

                return result

        # ========================================================
        # Normal yt-dlp engine
        # ========================================================

        return self.downloader.execute(
            config,
            cookies=COOKIES,
            progress_callback=progress_callback
        )


rz = SimpleSoup()

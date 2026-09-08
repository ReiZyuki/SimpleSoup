import inspect

from .parser import parse
from .downloader import Downloader
from .gallery import Gallery


# ============================================================
# SimpleSoup Configuration
# ============================================================

COOKIE_VARIABLE = "ReiZyuki"


class SimpleSoup:

    def __init__(self):
        self.downloader = Downloader()
        self.gallery = Gallery()

    def _get_user_cookies(self):

        # Get the caller's frame.
        # This allows:
        #
        # ReiZyuki = [
        #     "COOKIEPATH_1",
        #     "COOKIEPATH_2"
        # ]
        #
        # rz({...}, url)
        #
        # without requiring cookies=ReiZyuki.

        frame = inspect.currentframe()

        try:

            if frame is None:
                return []

            caller = frame.f_back

            # Walk upward until the user's scope is found.
            while caller is not None:
                cookies = caller.f_locals.get(COOKIE_VARIABLE)

                if cookies is None:
                    cookies = caller.f_globals.get(COOKIE_VARIABLE)

                if cookies is not None:
                    break

                caller = caller.f_back

            if caller is None:
                return []

            cookies = caller.f_locals.get(
                COOKIE_VARIABLE
            )

            if cookies is None:
                cookies = caller.f_globals.get(
                    COOKIE_VARIABLE
                )

            if cookies is None:
                return []

            if isinstance(cookies, str):
                return [cookies]

            if isinstance(cookies, (list, tuple)):
                return list(cookies)

            return []

        finally:

            del frame

    def __call__(
        self,
        expression,
        url=None,
        progress_callback=None
    ):

        cookies = self._get_user_cookies()

        return self.run(
            expression,
            url,
            progress_callback,
            cookies
        )

    def _find_working_cookie(self, url, cookies):

        if not cookies:
            return None

        print("Checking cookies...")

        for cookie in cookies:

            if not cookie:
                continue

            if not self.downloader.cookie_exists(cookie):

                print(
                    f"❌ Cookie file not found: {cookie}"
                )
                print("   → Continuing...")

                continue

            try:

                print(
                    f"🔍 Testing cookie: {cookie}"
                )

                self.downloader.test_cookie(
                    url,
                    cookie
                )

                print(
                    f"✅ Cookie works: {cookie}"
                )

                return cookie

            except Exception as e:

                print(
                    f"❌ Cookie failed: {cookie}"
                )

                print(
                    f"   → {e}"
                )

                print("   → Continuing...")

        print(
            "⚠️ No working cookie found."
        )

        return None

    def run(
        self,
        expression,
        url=None,
        progress_callback=None,
        cookies=None
    ):

        config = parse(expression)

        if url is not None:
            config["url"] = url

        if not config["url"]:
            raise ValueError("URL missing")

        cookie_list = cookies or []

        # ========================================================
        # FIRST: Normal request WITHOUT cookie
        # ========================================================

        try:

            return self._execute(
                config,
                None,
                progress_callback
            )

        except Exception as normal_error:

            print(
                "\n⚠️ Normal request failed."
            )

            # ====================================================
            # SECOND: Try user supplied ReiZyuki paths
            # ====================================================

            working_cookie = self._find_working_cookie(
                config["url"],
                cookie_list
            )

            if working_cookie is None:

                print(
                    "❌ No working cookie available."
                )

                raise normal_error

            print(
                f"🍪 Using working cookie: "
                f"{working_cookie}"
            )

            return self._execute(
                config,
                working_cookie,
                progress_callback
            )

    def _execute(
        self,
        config,
        cookies=None,
        progress_callback=None
    ):

        # ========================================================
        # Gallery-dl engine
        # ========================================================

        for block in config["blocks"]:

            if block["type"] == "gallery":

                result = self.gallery.execute(
                    config["url"],
                    cookies=cookies
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
            cookies=cookies,
            progress_callback=progress_callback
        )


rz = SimpleSoup()

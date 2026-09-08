import os
import subprocess


class Gallery:

    def __init__(self):
        self.path = "/storage/emulated/0/Download/ReiDownloader"
        os.makedirs(self.path, exist_ok=True)

    def execute(self, url, cookies=None):

        command = [
            "gallery-dl",
            "--directory",
            self.path,
        ]

        # ---------------------------------
        # Automatic cookies
        # ---------------------------------

        if cookies:

            if not os.path.isfile(cookies):
                raise FileNotFoundError(
                    f"Cookies file not found: {cookies}"
                )

            command.extend([
                "--cookies",
                cookies
            ])

        command.append(url)

        print("Downloading gallery...")

        subprocess.run(
            command,
            check=True
        )

        return self.path

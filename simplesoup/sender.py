import json
import mimetypes
import os

import requests


class Sender:
    def __init__(self, bot_token):
        if not bot_token:
            raise ValueError("bot_token is required.")

        self.bot_token = bot_token
        self.base_url = (
            f"https://api.telegram.org/bot{bot_token}"
        )

    def _request(self, method, data=None, files=None):
        response = requests.post(
            f"{self.base_url}/{method}",
            data=data,
            files=files,
            timeout=60,
        )

        response.raise_for_status()

        result = response.json()

        if not result.get("ok"):
            raise RuntimeError(
                result.get(
                    "description",
                    "Telegram API request failed.",
                )
            )

        return result["result"]

    def send_text(self, chat_id, text, buttons=None):
        data = {
            "chat_id": chat_id,
            "text": text,
        }

        if buttons:
            data["reply_markup"] = json.dumps(
                {
                    "inline_keyboard": [
                        [
                            {
                                "text": button["text"],
                                "url": button["url"],
                            }
                        ]
                        for button in buttons
                    ]
                }
            )

        return self._request(
            "sendMessage",
            data=data,
        )

    def send_media(
        self,
        chat_id,
        path,
        caption=None,
        buttons=None,
    ):
        path = self.validate_path(path)
        media_type = self.detect_media_type(path)

        if media_type == "image":
            method = "sendPhoto"
            field = "photo"
        elif media_type == "video":
            method = "sendVideo"
            field = "video"
        else:
            raise ValueError(
                f"Unsupported media type: {path}"
            )

        data = {
            "chat_id": chat_id,
        }

        if caption is not None:
            data["caption"] = caption

        if buttons:
            data["reply_markup"] = json.dumps(
                {
                    "inline_keyboard": [
                        [
                            {
                                "text": button["text"],
                                "url": button["url"],
                            }
                        ]
                        for button in buttons
                    ]
                }
            )

        with open(path, "rb") as media_file:
            return self._request(
                method,
                data=data,
                files={
                    field: media_file,
                },
            )

    @staticmethod
    def validate_path(path):
        if not isinstance(path, (str, os.PathLike)):
            raise TypeError(
                "Media path must be a string or path-like value."
            )

        path = os.fspath(path)

        if not os.path.isfile(path):
            raise FileNotFoundError(path)

        return path

    @staticmethod
    def detect_media_type(path):
        mime_type, _ = mimetypes.guess_type(path)

        if not mime_type:
            raise ValueError(
                f"Cannot detect media type: {path}"
            )

        if mime_type.startswith("image/"):
            return "image"

        if mime_type.startswith("video/"):
            return "video"

        raise ValueError(
            f"Unsupported media type: {mime_type}"
        )

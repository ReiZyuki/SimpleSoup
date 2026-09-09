import os

from .sender import Sender
from .sender_parser import SenderParser
from .sender_runtime import SenderRuntime


class SenderExecutor:
    def __init__(self, bot_token, variables=None):
        self.sender = Sender(bot_token)
        self.runtime = SenderRuntime(variables)

    def execute(self, source, chat_id):
        entries = SenderParser.parse(source)

        media_paths = []
        text_parts = []
        buttons = []

        for entry in entries:
            entry_type = entry["type"]

            if entry_type == "expression":
                expression = entry["expression"]

                if expression == "user":
                    if entry["value"]:
                        text_parts.append(str(entry["value"]))
                    continue

                if expression == "path":
                    if not entry["value"]:
                        raise ValueError(
                            "{path} requires a media path."
                        )

                    path = self.runtime.validate_path(
                        entry["value"]
                    )

                    media_paths.append(path)
                    continue

                resolved = self.runtime.resolve(expression)

                for item in resolved["value"]:
                    value = item["value"]

                    if self._is_media_file(value):
                        media_paths.append(
                            os.fspath(value)
                        )
                    else:
                        text_parts.append(
                            self._format_item(item)
                        )

            elif entry_type == "button":
                button = entry.get("button")

                if not button:
                    raise ValueError(
                        "Invalid inline button definition."
                    )

                buttons.append(button)

            elif entry_type == "raw":
                value = entry.get("value")

                if value:
                    text_parts.append(str(value))

        text = "\n".join(
            part for part in text_parts if part
        ).strip()

        if len(media_paths) > 1:
            raise ValueError(
                "Only one media item can be sent in one sender expression."
            )

        if media_paths:
            return self.sender.send_media(
                chat_id=chat_id,
                path=media_paths[0],
                caption=text or None,
                buttons=buttons or None,
            )

        if text:
            return self.sender.send_text(
                chat_id=chat_id,
                text=text,
                buttons=buttons or None,
            )

        raise ValueError(
            "Sender expression contains no sendable content."
        )

    @staticmethod
    def _is_media_file(value):
        if not isinstance(value, (str, os.PathLike)):
            return False

        path = os.fspath(value)

        if not os.path.isfile(path):
            return False

        try:
            Sender.detect_media_type(path)
            return True
        except (ValueError, TypeError):
            return False

    @staticmethod
    def _format_item(item):
        value = item["value"]

        if item["label"] is not None:
            return f'{item["label"]}{value}'

        return str(value)

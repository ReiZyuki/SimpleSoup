import os
import json
import inspect
import requests

from simplesoup import rz


_STORE = {}


def _extract(result, key):
    if isinstance(result, dict):
        if key in result:
            return result[key]

        for value in result.values():
            found = _extract(value, key)
            if found is not None:
                return found

    elif isinstance(result, (list, tuple)):
        for value in result:
            found = _extract(value, key)
            if found is not None:
                return found

    return None


def _store_rz_variables(expression, result, frame):
    if not isinstance(expression, dict):
        return

    values = {}

    for source_key, variable_name in expression.items():
        if not isinstance(variable_name, str) or not variable_name:
            continue

        if isinstance(result, dict) and variable_name in result:
            value = result[variable_name]
        elif source_key.startswith("video["):
            value = _extract(result, "video")
        else:
            value = _extract(result, source_key)

        if value is None:
            continue

        _STORE[variable_name] = value
        values[variable_name] = value

    if values:
        frame.f_globals.update(values)


_original_rz_run = rz.run


def _rz_run_bridge(self, expression, url=None, progress_callback=None, cookies=None):
    caller = inspect.currentframe().f_back

    try:
        result = _original_rz_run(
            expression,
            url=url,
            progress_callback=progress_callback,
            cookies=cookies,
        )

        _store_rz_variables(
            expression,
            result,
            caller,
        )

        return result

    finally:
        del caller


_rz_run_bridge._simplesoup_sender_bridge = True

if not getattr(rz.run, "_simplesoup_sender_bridge", False):
    rz.run = _rz_run_bridge.__get__(rz, type(rz))


def _resolve(value):
    if not isinstance(value, str):
        return value

    for name, stored_value in _STORE.items():
        value = value.replace(
            "{" + name + "}",
            str(stored_value),
        )

    return value


def _buttons(button):
    if not button:
        return None

    keyboard = []

    for name, url in button.items():
        keyboard.append([
            {
                "text": str(name),
                "url": _resolve(url),
            }
        ])

    return {
        "inline_keyboard": keyboard
    }


def _token():
    frame = inspect.currentframe().f_back

    try:
        while frame:
            token = frame.f_globals.get("BOT_TOKEN")

            if token:
                return str(token)

            token = frame.f_locals.get("BOT_TOKEN")

            if token:
                return str(token)

            frame = frame.f_back

    finally:
        del frame

    raise ValueError("BOT_TOKEN was not found.")


def _telegram(method, data=None, files=None):
    url = f"https://api.telegram.org/bot{_token()}/{method}"
    r = requests.post(url, data=data or {}, files=files, timeout=(30, 300))
    r.raise_for_status()
    result = r.json()
    if not result.get("ok"):
        raise RuntimeError(result.get("description", "Telegram API request failed."))
    return result


def ro(data, chat_id):
    if not isinstance(data, dict):
        raise TypeError("Sender data must be a dictionary.")
    if chat_id is None:
        raise ValueError("chat_id is required.")

    media = _resolve(data.get("media", ""))
    caption = _resolve(data.get("caption", ""))
    thumbnail = _resolve(data.get("thumbnail", ""))
    markup = _buttons(data.get("button"))

    if not media:
        payload = {"chat_id": chat_id, "text": caption}
        if markup:
            payload["reply_markup"] = json.dumps(markup)
        return _telegram("sendMessage", data=payload)

    media = os.fspath(media)
    if not os.path.isfile(media):
        raise FileNotFoundError(media)

    payload = {"chat_id": chat_id}
    if caption:
        payload["caption"] = caption
    if markup:
        payload["reply_markup"] = json.dumps(markup)

    extension = os.path.splitext(media)[1].lower()

    if extension in {".jpg", ".jpeg", ".png", ".webp"}:
        with open(media, "rb") as file:
            return _telegram("sendPhoto", data=payload, files={"photo": file})

    if extension in {".mp3", ".m4a", ".aac", ".ogg", ".wav", ".flac"}:
        with open(media, "rb") as file:
            return _telegram("sendAudio", data=payload, files={"audio": file})

    with open(media, "rb") as file:
        if thumbnail:
            thumbnail = os.fspath(thumbnail)
            if os.path.isfile(thumbnail):
                with open(thumbnail, "rb") as thumb:
                    return _telegram("sendVideo", data=payload, files={"video": file, "thumbnail": thumb})
        return _telegram("sendVideo", data=payload, files={"video": file})

STAGES = {
    0: "audio",
    1: "360p",
    2: "480p",
    3: "720p",
    4: "1080p",
    5: "best",
}


def parse(expression):
    """
    Parse SimpleSoup configuration.

    Supported format:

        {
            "video[4]": "video",
            "playlist": "4:10:4",
            "title": "title",
            "creator": "creator",
            "url": "url",
            "views": "views",
            "likes": "likes",
            "count": "count",
            "time": "duration",
            "thumbnail": "thumbnail"
        }

    Playlist format:

        "playlist": "quality:skip:count"

    Example:

        "playlist": "4:10:4"

    Means:

        4  = 720p
        10 = skip first 10 videos
        4  = download next 4 videos

    Old rz.(...) syntax is also supported.
    """

    # -----------------------------
    # New dictionary-style syntax
    # -----------------------------
    if isinstance(expression, dict):

        result = {
            "url": None,
            "blocks": []
        }

        for key, variable in expression.items():

            key = str(key).strip()
            variable = str(variable).strip()

            # video[4]
            if key.startswith("video[") and key.endswith("]"):

                stage_text = key[6:-1]

                try:
                    stage = int(stage_text)
                except ValueError:
                    raise ValueError(
                        f"Invalid video stage: {stage_text}"
                    )

                if stage not in STAGES:
                    raise ValueError(
                        f"Unknown video stage: {stage}"
                    )

                result["blocks"].append({
                    "type": "video",
                    "stage": stage,
                    "variable": variable
                })

                continue

            # playlist
            if key == "playlist":

                parts = variable.split(":")

                if len(parts) != 3:
                    raise ValueError(
                        "Playlist syntax: playlist:quality:skip:count"
                    )

                try:
                    quality = int(parts[0])
                    skip = int(parts[1])
                    count = int(parts[2])
                except ValueError:
                    raise ValueError(
                        "Playlist values must be numbers"
                    )

                if quality not in STAGES:
                    raise ValueError(
                        f"Unknown playlist quality: {quality}"
                    )

                if skip < 0:
                    raise ValueError(
                        "Playlist skip cannot be negative"
                    )

                if count <= 0:
                    raise ValueError(
                        "Playlist count must be greater than 0"
                    )

                result["blocks"].append({
                    "type": "playlist",
                    "quality": quality,
                    "skip": skip,
                    "count": count,
                    "variable": None
                })

                continue

            # normal block
            result["blocks"].append({
                "type": key,
                "variable": variable
            })

        return result

    # -----------------------------
    # Old rz.(...) syntax
    # -----------------------------
    expression = expression.strip()

    if not expression.startswith("rz.(") or not expression.endswith(")"):
        raise ValueError("Invalid SimpleSoup syntax")

    body = expression[4:-1].strip()

    parts = [
        p.strip()
        for p in body.split(";")
        if p.strip()
    ]

    result = {
        "url": None,
        "blocks": []
    }

    for part in parts:

        # URL
        if part.startswith("{") and part.endswith("}"):
            result["url"] = part[1:-1].strip()
            continue

        # video[4]:variable
        if part.startswith("video["):

            if "]:" not in part:
                raise ValueError(
                    "Video syntax: video[stage]:variable"
                )

            stage_text, variable = part.split("]:", 1)

            try:
                stage = int(stage_text[6:])
            except ValueError:
                raise ValueError(
                    "Invalid video stage"
                )

            if stage not in STAGES:
                raise ValueError(
                    f"Unknown video stage: {stage}"
                )

            result["blocks"].append({
                "type": "video",
                "stage": stage,
                "variable": variable.strip()
            })

            continue

        # name:variable
        if ":" in part:

            name, variable = part.split(":", 1)

            result["blocks"].append({
                "type": name.strip(),
                "variable": variable.strip()
            })

            continue

        # simple block
        result["blocks"].append({
            "type": part,
            "variable": None
        })

    if not result["url"]:
        raise ValueError("URL missing")

    return result

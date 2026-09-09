import re


class SenderParser:
    VARIABLE_PATTERN = re.compile(
        r'^\{\s*(.*?)\s*\}$',
        re.DOTALL,
    )

    BUTTON_PATTERN = re.compile(
        r'^[A-Za-z]$',
    )

    @classmethod
    def parse(cls, source):
        if not isinstance(source, str):
            raise TypeError("Sender source must be a string.")

        source = source.strip()

        if not source.startswith("f{") or not source.endswith("}"):
            raise SyntaxError(
                "Invalid SimpleSoup sender syntax."
            )

        body = source[2:-1].strip()

        if not body:
            return []

        return [
            parsed
            for entry in cls._split_entries(body)
            if (parsed := cls._parse_entry(entry)) is not None
        ]

    @classmethod
    def _parse_entry(cls, entry):
        entry = entry.strip()

        if not entry:
            return None

        # -------------------------------------------------
        # BUTTON
        # "A": "TEXT": "URL"
        # -------------------------------------------------
        if entry.startswith('"') and cls._is_button_entry(entry):
            parts = cls._split_button(entry)

            if len(parts) != 3:
                raise SyntaxError(
                    f"Invalid inline button syntax: {entry}"
                )

            key = cls._strip_quotes(parts[0])
            text = cls._strip_quotes(parts[1])
            url = cls._strip_quotes(parts[2])

            if not cls.BUTTON_PATTERN.fullmatch(key):
                raise SyntaxError(
                    f"Invalid button identifier: {key}"
                )

            if not text:
                raise SyntaxError(
                    "Button text cannot be empty."
                )

            if not url:
                raise SyntaxError(
                    "Button URL cannot be empty."
                )

            return {
                "type": "button",
                "id": key,
                "button": {
                    "text": text,
                    "url": url,
                },
            }

        # -------------------------------------------------
        # EXPRESSION
        # "{media}":,
        # "{title}":,
        # "{("TITLE: ")title,...}":,
        # -------------------------------------------------
        if entry.startswith('"'):
            key, value = cls._split_expression(entry)

            variable_match = cls.VARIABLE_PATTERN.fullmatch(key)

            if variable_match:
                return {
                    "type": "expression",
                    "expression": variable_match.group(1).strip(),
                    "value": value,
                }

        raise SyntaxError(
            f"Invalid sender expression: {entry}"
        )

    @staticmethod
    def _split_entries(body):
        entries = []
        current = []

        brace_depth = 0
        paren_depth = 0
        bracket_depth = 0

        quote = None
        escape = False

        for char in body:
            if escape:
                current.append(char)
                escape = False
                continue

            if char == "\\":
                current.append(char)
                escape = True
                continue

            if quote is not None:
                current.append(char)

                if char == quote:
                    quote = None

                continue

            if char in ('"', "'"):
                quote = char
                current.append(char)
                continue

            if char == "{":
                brace_depth += 1

            elif char == "}":
                brace_depth -= 1

            elif char == "(":
                paren_depth += 1

            elif char == ")":
                paren_depth -= 1

            elif char == "[":
                bracket_depth += 1

            elif char == "]":
                bracket_depth -= 1

            if (
                char == ","
                and brace_depth == 0
                and paren_depth == 0
                and bracket_depth == 0
            ):
                item = "".join(current).strip()

                if item:
                    entries.append(item)

                current = []
                continue

            current.append(char)

        item = "".join(current).strip()

        if item:
            entries.append(item)

        return entries

    @staticmethod
    def _split_expression(entry):
        # Find the closing quote belonging to the OUTER key.
        #
        # Example:
        # "{("TITLE: ")title,("CREATOR: ")creator}":
        #
        # The quotes inside {...} are part of the expression
        # and must NOT terminate the key.

        if not entry.startswith('"'):
            raise SyntaxError(
                f"Invalid expression: {entry}"
            )

        brace_start = entry.find("{", 1)

        if brace_start == -1:
            raise SyntaxError(
                f"Invalid expression: {entry}"
            )

        brace_end = SenderParser._find_matching_brace(
            entry,
            brace_start,
        )

        if brace_end == -1:
            raise SyntaxError(
                f"Unclosed expression: {entry}"
            )

        cursor = brace_end + 1

        if cursor >= len(entry) or entry[cursor] != '"':
            raise SyntaxError(
                f"Invalid expression key: {entry}"
            )

        key = entry[1:brace_end + 1]

        cursor += 1

        while (
            cursor < len(entry)
            and entry[cursor].isspace()
        ):
            cursor += 1

        if cursor >= len(entry) or entry[cursor] != ":":
            raise SyntaxError(
                f"Missing ':' after expression: {entry}"
            )

        value = entry[cursor + 1:].strip()

        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]

        return key, value

    @staticmethod
    def _split_button(entry):
        parts = []
        current = []

        quote = None
        escape = False

        for char in entry:
            if escape:
                current.append(char)
                escape = False
                continue

            if char == "\\":
                current.append(char)
                escape = True
                continue

            if char in ('"', "'"):
                if quote is None:
                    quote = char

                elif quote == char:
                    quote = None

                current.append(char)
                continue

            if char == ":" and quote is None:
                parts.append("".join(current).strip())
                current = []
                continue

            current.append(char)

        parts.append("".join(current).strip())

        return parts

    @staticmethod
    def _is_button_entry(entry):
        if not entry.startswith('"'):
            return False

        end = entry.find('"', 1)

        if end == -1:
            return False

        key = entry[1:end]

        return bool(
            SenderParser.BUTTON_PATTERN.fullmatch(key)
        )

    @staticmethod
    def _find_matching_brace(source, opening):
        depth = 1

        for index in range(opening + 1, len(source)):
            char = source[index]

            if char == "{":
                depth += 1

            elif char == "}":
                depth -= 1

                if depth == 0:
                    return index

        return -1

    @staticmethod
    def _strip_quotes(value):
        value = value.strip()

        if len(value) >= 2:
            if (
                value[0] == value[-1]
                and value[0] in ('"', "'")
            ):
                return value[1:-1]

        return value

import os
import re

from .sender_context import SenderContext


class SenderRuntime:
    LABEL_PATTERN = re.compile(
        r'^\(\s*"([^"]*)"\s*\)(.+)$',
        re.DOTALL,
    )

    def __init__(self, variables=None, context=None):
        if context is not None:
            self.context = context
        else:
            self.context = SenderContext(variables)

    def set_variables(self, variables):
        self.context.update(variables)

    def set(self, name, value):
        self.context.set(name, value)

    def get(self, name):
        return self.context.get(name)

    def resolve(self, expression):
        expression = expression.strip()

        if expression == "user":
            return {
                "type": "user",
                "value": None,
            }

        if expression == "path":
            return {
                "type": "path",
                "value": None,
            }

        variables = self._split_variables(expression)
        resolved = []

        for item in variables:
            item = item.strip()

            if not item:
                continue

            label_match = self.LABEL_PATTERN.fullmatch(item)

            if label_match:
                label = label_match.group(1)
                variable_name = label_match.group(2).strip()

                if not variable_name:
                    raise SyntaxError(
                        "Variable name is missing after label."
                    )

                value = self.get(variable_name)

                resolved.append({
                    "label": label,
                    "variable": variable_name,
                    "value": value,
                })
            else:
                value = self.get(item)

                resolved.append({
                    "label": None,
                    "variable": item,
                    "value": value,
                })

        return {
            "type": "variables",
            "value": resolved,
        }

    @staticmethod
    def format_variables(values):
        output = []

        for item in values:
            value = item["value"]

            if item["label"] is not None:
                output.append(
                    f'{item["label"]}{value}'
                )
            else:
                output.append(str(value))

        return "\n".join(output)

    @staticmethod
    def validate_path(path):
        if not isinstance(path, (str, os.PathLike)):
            raise TypeError(
                "Path must be a string or path-like value."
            )

        path = os.fspath(path)

        if not os.path.isfile(path):
            raise FileNotFoundError(path)

        return path

    @staticmethod
    def _split_variables(expression):
        parts = []
        current = []

        paren_depth = 0
        quote = None
        escape = False

        for char in expression:
            if escape:
                current.append(char)
                escape = False
                continue

            if char == "\\":
                current.append(char)
                escape = True
                continue

            if quote:
                current.append(char)

                if char == quote:
                    quote = None

                continue

            if char == '"':
                quote = char
                current.append(char)
                continue

            if char == "(":
                paren_depth += 1
            elif char == ")":
                paren_depth -= 1

            if char == "," and paren_depth == 0:
                part = "".join(current).strip()

                if part:
                    parts.append(part)

                current = []
                continue

            current.append(char)

        part = "".join(current).strip()

        if part:
            parts.append(part)

        return parts

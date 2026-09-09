import ast


class SenderPreprocessor(ast.NodeTransformer):
    @classmethod
    def process(cls, source):
        if not isinstance(source, str):
            raise TypeError("Source must be a string.")

        tree = ast.parse(source)

        tree = cls().visit(tree)
        ast.fix_missing_locations(tree)

        return ast.unparse(tree)

    def visit_Call(self, node):
        self.generic_visit(node)

        if not self._is_ro(node):
            return node

        if len(node.args) != 2:
            return node

        data = node.args[0]

        if not isinstance(data, ast.Dict):
            return node

        node.args[0] = self._replace_fstrings(data)

        return node

    @staticmethod
    def _is_ro(node):
        return (
            isinstance(node.func, ast.Name)
            and node.func.id == "ro"
        )

    def _replace_fstrings(self, node):
        for index, value in enumerate(node.values):
            node.values[index] = self._replace_value(value)

        return node

    def _replace_value(self, node):
        if isinstance(node, ast.JoinedStr):
            return self._fstring_to_marker(node)

        if isinstance(node, ast.Dict):
            return self._replace_fstrings(node)

        if isinstance(node, (ast.List, ast.Tuple)):
            node.elts = [
                self._replace_value(item)
                for item in node.elts
            ]

        return node

    @staticmethod
    def _fstring_to_marker(node):
        parts = []

        for value in node.values:
            if isinstance(value, ast.Constant):
                parts.append(str(value.value))

            elif isinstance(value, ast.FormattedValue):
                if isinstance(value.value, ast.Name):
                    parts.append(
                        "{" + value.value.id + "}"
                    )
                else:
                    parts.append(
                        ast.unparse(value.value)
                    )

        return ast.Constant(
            value="".join(parts)
        )

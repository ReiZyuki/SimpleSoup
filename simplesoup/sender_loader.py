import ast

from .sender_preprocessor import SenderPreprocessor


class SenderLoader:

    @staticmethod
    def transform(source):
        if not isinstance(source, str):
            raise TypeError("Source must be a string.")

        transformed = SenderPreprocessor.process(source)

        ast.parse(transformed)

        return transformed

    @classmethod
    def compile(cls, source, filename="<simplesoup>"):
        transformed = cls.transform(source)

        return compile(
            transformed,
            filename,
            "exec",
        )

    @classmethod
    def execute(cls, source, namespace=None, filename="<simplesoup>"):
        code = cls.compile(
            source,
            filename=filename,
        )

        if namespace is None:
            namespace = {}

        exec(code, namespace, namespace)

        return namespace

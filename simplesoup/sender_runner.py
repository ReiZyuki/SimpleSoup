from .sender import Sender
from .sender_context import SenderContext
from .sender_loader import SenderLoader


class SenderRunner:
    def __init__(self, bot_token, namespace=None):
        self.sender = Sender(bot_token)
        self.context = SenderContext(namespace)

    def run(
        self,
        source,
        namespace=None,
        filename="<simplesoup>",
    ):
        if namespace is not None:
            self.context.update(namespace)

        runtime_namespace = self.context.snapshot()
        runtime_namespace["ro"] = self._ro

        return SenderLoader.execute(
            source=source,
            namespace=runtime_namespace,
            filename=filename,
        )

    def _ro(self, data, chat_id):
        from .sender_executor import SenderExecutor

        executor = SenderExecutor(
            bot_token=self.sender.bot_token,
            variables=self.context.snapshot(),
        )

        return executor.execute(
            source=data,
            chat_id=chat_id,
        )

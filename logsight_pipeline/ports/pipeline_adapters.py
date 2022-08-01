from logsight.analytics_core.logs import LogBatch
from logsight.connectors.base.adapter import AdapterError, SourceAdapter
from logsight.connectors.base.mixins import ConnectableConnector
from logsight.connectors.base.connectable import Connectable


class PipelineSourceAdapter(SourceAdapter, ConnectableConnector):
    def _connect(self):
        if isinstance(self.connector, Connectable):
            self.connector.connect()

    def close(self):
        if isinstance(self.connector, ConnectableConnector):
            self.connector.close()

    def receive(self) -> LogBatch:
        message = self.connector.receive_message()
        try:
            log_batch = self.serializer.deserialize(message)
        except KeyError:
            raise AdapterError("Cannot deserialize message $m")
        return log_batch

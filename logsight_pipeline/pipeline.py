import logging
import threading
import time
import uuid
from typing import Dict, Optional, Union

from logsight.connectors.base.adapter import AdapterError
from logsight.connectors.base.connectable import Connectable
from logsight.services.service_provider import ServiceProvider
from logsight_pipeline.modules.core import Module
from logsight_pipeline.modules.core.module import ConnectableModule
from logsight_pipeline.ports.pipeline_adapters import PipelineSourceAdapter

logger = logging.getLogger("logsight." + __name__)


class Pipeline:
    """ A pipeline is a collection of modules that are connected together..."""
    _id = uuid.uuid4()

    def __init__(self, modules: Dict[str, Union[Module, ConnectableModule]], input_module: Module,
                 data_source: PipelineSourceAdapter,
                 control_source: Optional[PipelineSourceAdapter] = None,
                 metadata: Optional[Dict] = None):
        self.control_source = control_source
        self.data_source = data_source
        self.input_module = input_module
        self.modules = modules
        self.metadata = metadata
        self.storage = ServiceProvider.provide_postgres()

    def run(self):
        """
        Run the pipeline. The pipeline and its modules connect to external endpoints before the pipeline starts
        receiving messages from the data source.
        """
        self._connect()
        self._start_receiving()

    def _connect(self):
        """
        The function connects the data source, control source, and modules
        """
        # connect data source
        if isinstance(self.data_source.connector, Connectable):
            self.data_source.connector.connect()
        # connect control source
        if self.control_source and isinstance(self.control_source.connector, Connectable):
            self.control_source.connector.connect()
        # connect modules
        for module in self.modules.values():
            if isinstance(module, ConnectableModule) and isinstance(module.connector, Connectable):
                module.connector.connect()

    def _start_receiving(self):
        """
        It starts a thread that listens for control messages, and then it loops over the data source, receiving messages and
        passing them to the input module
        """
        if self.control_source:
            internal = threading.Thread(name=str(self), target=self._start_control_listener, daemon=True)
            internal.setDaemon(True)
            internal.start()
        total = 0
        total_t = 0
        while self.data_source.has_next():
            try:
                log_batch = self.data_source.receive()
                log_count = len(log_batch.logs)
                logger.debug(f"Received Batch {log_batch.id}")
                t = time.perf_counter()
                self.input_module.handle(log_batch)
                total += log_count
                total_t += time.perf_counter() - t
                logger.debug(f"Processed {log_count} logs in {time.perf_counter() - t}")
                logger.debug(f"Total:{total} time: {total_t}")
                self.storage.update_log_receipt(log_batch.id, log_count)
            except AdapterError:
                continue
        self._close()

    def _close(self):
        """
        The function calls close on every module
        """
        for module in self.modules.values():
            if isinstance(module, ConnectableModule):
                if isinstance(module.connector, Connectable):
                    module.connector.close()

    def _start_control_listener(self):
        """
        The function starts a thread that listens for control messages from the control source
        """
        logger.info("Pipeline is ready to receive control messages.")
        while self.control_source.has_next():
            msg = self.control_source.receive()
            logger.debug(f"Pipeline received control message: {msg}")
            self._process_control_message(msg)
        logger.debug("Control message receiving thread terminated.")

    @staticmethod
    def _process_control_message(msg):
        return msg

    def __repr__(self):
        return f"Pipeline ({self._id})"

    @property
    def id(self):
        return self._id

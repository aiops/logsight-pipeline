from unittest.mock import MagicMock

import pytest
from dacite import from_dict

from logsight.analytics_core.logs import LogBatch
from logsight.common.helpers import to_flat_dict
from logsight.connectors.sinks import PrintSink
from logsight_pipeline.modules.data_store import LogStoreModule, BatchMetadataStoreModule


@pytest.fixture(scope="module")
def log_batch():
    return from_dict(data={"logs": [{"timestamp": "2020-01-01", "message": "Hello World", "level": "INFO"}],
                           "index": "test_index"}, data_class=LogBatch)


def test_process(log_batch):
    store = LogStoreModule(PrintSink())
    store.connector.send = MagicMock()
    processed = [to_flat_dict(log) for log in log_batch.logs]

    store.process(log_batch)

    store.connector.send.assert_called_once_with(processed, target="_".join([log_batch.index, "pipeline"]))


def test_process_batch(log_batch):
    store = BatchMetadataStoreModule(PrintSink(), index_ext="test")
    store.connector.send = MagicMock()
    _ = [to_flat_dict(log) for log in log_batch.logs]

    store.process(log_batch)

    store.connector.send.assert_called_once_with(log_batch.metadata, target="_".join([log_batch.index, "test"]))

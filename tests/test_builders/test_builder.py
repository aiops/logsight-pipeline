import pytest

from logsight.connectors import ConnectableConnector
from logsight.connectors.builders.properties import AdapterConfigProperties, ConnectorConfigProperties
from logsight_pipeline.builders.adapter_builder import PipelineAdapterBuilder
from logsight_pipeline.ports.pipeline_adapters import PipelineSourceAdapter


@pytest.fixture
def valid_source():
    yield ConnectorConfigProperties(connector_type="source", connection="file")


def test_build_pipeline_source(valid_source):
    adapter_config = AdapterConfigProperties(connector=valid_source)
    builder = PipelineAdapterBuilder()
    connection = builder.build(adapter_config)

    assert isinstance(connection, PipelineSourceAdapter)
    if hasattr(connection, 'connect') and hasattr(connection, 'close'):
        assert isinstance(connection, ConnectableConnector)

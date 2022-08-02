from unittest import mock
from unittest.mock import MagicMock, Mock

import pytest

from logsight.connectors.builders.properties import AdapterConfigProperties, ConnectorConfigProperties
from logsight.connectors.connectors.elasticsearch import ElasticsearchConfigProperties
from logsight.analytics_core.logs import LogBatch, LogsightLog
from dacite import from_dict
from logsight_pipeline.builders.pipeline_builder import PipelineBuilder
from logsight_pipeline.configs.configuration import PipelineConfig
from logsight_pipeline.modules.core import ConnectableModule
from elasticsearch import helpers

from logsight.services.elasticsearch_service.elasticsearch_service import ElasticsearchService
from logsight.services.service_provider import ServiceProvider


@pytest.fixture
def pipeline():
    pipeline_cfg = PipelineConfig()
    builder = PipelineBuilder()
    pipeline = builder.build(pipeline_cfg.pipeline)
    yield pipeline


@pytest.fixture
def pipeline_with_control():
    pipeline_cfg = PipelineConfig().pipeline_config
    pipeline_cfg.connectors.control_source = AdapterConfigProperties(
        connector=ConnectorConfigProperties("source", "file"))
    # Add control source

    builder = PipelineBuilder()
    pipeline = builder.build(pipeline_cfg)
    yield pipeline


# noinspection PyUnresolvedReferences
def test_run(pipeline):
    pipeline.control_source = MagicMock()
    pipeline.data_source.receive = MagicMock(
        return_value=LogBatch(logs=[
            LogsightLog(**{"timestamp": "2020-01-01", "message": "Hello World", "level": "INFO"})],
            index="test_index")
    )
    pipeline.data_source.has_next = MagicMock(side_effect=[True, False])
    if 'log_ad' in pipeline.modules:
        pipeline.modules['log_ad'].ad.model.predict = MagicMock(return_value=[0], side_effect=[[0]])
    for module_name in pipeline.modules:
        if isinstance(pipeline.modules[module_name], ConnectableModule):
            pipeline.modules[module_name].connector = MagicMock(sepc=pipeline.modules[module_name].connector)
            pipeline.modules[module_name].connector.connect = MagicMock()
            pipeline.modules[module_name].connector.send = MagicMock()

    es = ElasticsearchService(ElasticsearchConfigProperties())
    es._connect = MagicMock()
    es.get_all_templates_for_index = MagicMock(return_value=[])
    ServiceProvider.provide_elasticsearch = MagicMock(return_value=es)

    pipeline.data_source.has_next = Mock(side_effect=[True, False])
    helpers.parallel_bulk = MagicMock()
    pipeline.data_source.connect = MagicMock()
    pipeline.storage = MagicMock()

    with mock.patch("threading.Thread"):
        pipeline.run()


def test_start_control_listener(pipeline):
    pipeline.control_source = MagicMock()
    pipeline.control_source.has_next = MagicMock(side_effect=[True, False])
    pipeline.control_source.receive = MagicMock(return_value="Control message")

    pipeline._start_control_listener()

    pipeline.control_source.has_next.assert_called()
    assert pipeline.control_source.has_next.call_count == 2
    assert pipeline.control_source.receive.call_count == 1


def test__process_control_message(pipeline):
    message = "Test message"
    result = pipeline._process_control_message(message)
    assert result == message


def test_id(pipeline):
    assert pipeline.id == pipeline._id

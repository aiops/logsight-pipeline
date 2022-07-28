import pytest

from logsight.common.patterns.builder import BuilderException
from logsight.connectors.builders.properties import AdapterConfigProperties, ConnectorConfigProperties
from logsight.connectors.sources import StdinSource
from logsight_pipeline.builders.pipeline_builder import PipelineBuilder
from logsight_pipeline.config.properties import ModuleConfigProperties, PipelineConnectorsProperties, PipelineProperties
from logsight_pipeline.modules import AnomalyDetectionModule, LogStoreModule, LogParserModule


@pytest.fixture
def valid_pipeline_cfg():
    ad_config = ModuleConfigProperties(classname="AnomalyDetectionModule", next_module="sink")
    parse_config = ModuleConfigProperties(classname="LogParserModule", next_module="ad")
    sink_config = ModuleConfigProperties(classname="LogStoreModule",
                                         args={"connector": {"connection": "stdout", "connector_type": "sink"}})
    yield PipelineProperties(
        connectors=PipelineConnectorsProperties(
            data_source=AdapterConfigProperties(
                ConnectorConfigProperties(connector_type="source", connection="stdin"))),
        modules={"ad": ad_config, "sink": sink_config, "parse": parse_config})


@pytest.fixture
def module_not_connected_cfg():
    ad_config = ModuleConfigProperties(classname="AnomalyDetectionModule", next_module="sink")
    parse_config = ModuleConfigProperties(classname="LogParserModule")
    sink_config = ModuleConfigProperties(classname="LogStoreModule",
                                         args={
                                             "connector": {
                                                 "connection": "stdout",
                                                 "connector_type": "sink",
                                                 "params": {}
                                             }})
    yield PipelineProperties(
        connectors=PipelineConnectorsProperties(
            data_source=AdapterConfigProperties(
                ConnectorConfigProperties(
                    connector_type="source",
                    connection="file"))),
        modules={"ad": ad_config, "sink": sink_config, "parse": parse_config})


def test_build(valid_pipeline_cfg):
    builder = PipelineBuilder()
    pipeline = builder.build(valid_pipeline_cfg)
    assert isinstance(pipeline.data_source.connector, StdinSource)
    assert len(pipeline.modules) == 3
    assert isinstance(pipeline.modules['ad'], AnomalyDetectionModule)
    assert isinstance(pipeline.modules['parse'], LogParserModule)
    assert isinstance(pipeline.modules['sink'], LogStoreModule)


def test_build_fail(module_not_connected_cfg):
    builder = PipelineBuilder()
    pytest.raises(BuilderException, builder.build, module_not_connected_cfg)

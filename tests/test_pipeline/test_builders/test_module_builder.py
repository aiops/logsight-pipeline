import pytest

from logsight.connectors import ConnectableConnector
from logsight_pipeline.builders.module_builder import ModuleBuilder
from logsight_pipeline.config.properties import ModuleConfigProperties
from logsight_pipeline.modules.core import ConnectableModule


@pytest.fixture(ids=["anomaly_detection", "fork", "log_parsing"],
                params=["AnomalyDetectionModule",
                        "ForkModule",
                        "LogParserModule",
                        ])
def valid_module_cfg(request):
    yield ModuleConfigProperties(classname=request.param, args={})


def test_build_module(valid_module_cfg):
    module_builder = ModuleBuilder()
    module = module_builder.build(valid_module_cfg)
    assert module.__class__.__name__ == valid_module_cfg.classname


def test_build_module_with_connector():
    module_builder = ModuleBuilder()
    module = module_builder.build(
        ModuleConfigProperties(classname="LogStoreModule",
                               args={
                                   "connector": {
                                       "connection": "elasticsearch",
                                       "connector_type": "sink",
                                       "params": {}
                                   }}))
    assert module.__class__.__name__ == "LogStoreModule"
    assert isinstance(module, ConnectableModule) is True
    assert isinstance(module.connector, ConnectableConnector) is True

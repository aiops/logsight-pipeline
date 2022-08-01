import pytest

from logsight_pipeline.ports.pipeline_adapters import PipelineSourceAdapter


@pytest.fixture
def adapter():
    yield PipelineSourceAdapter()


def test_pipeline_adapter(adapter):
    pass

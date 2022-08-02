import os
from pathlib import Path
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator

from logsight.configs.properties import ConfigProperties
from logsight.connectors.builders.properties import AdapterConfigProperties


class MetadataConfigProperties(BaseModel):
    input_module: str
    kafka_topics: Optional[List[str]] = Field(default_factory=list)


class ModuleConfigProperties(BaseModel):
    classname: str
    args: Optional[Dict] = Field(default_factory=dict)
    next_module: Optional[Union[str, List[str]]] = None


class PipelineConnectorsProperties(BaseModel):
    data_source: AdapterConfigProperties
    control_source: Optional[AdapterConfigProperties] = None


@ConfigProperties(prefix="pipeline",
                  path=Path(os.path.dirname(os.path.realpath(__file__))) / "pipeline.cfg")
class PipelineProperties(BaseModel):
    modules: Dict[str, ModuleConfigProperties]
    connectors: PipelineConnectorsProperties
    metadata: Optional[Dict] = Field(default_factory=dict)


# noinspection PyMethodParameters
@ConfigProperties(prefix="pipeline",
                  path=Path(os.path.dirname(os.path.realpath(__file__))) / "logsight_pipeline_config.cfg")
class LogsightPipelineConfigProperties(BaseModel):
    pipeline_index_ext: str = "pipeline"
    pipeline_connection: str = "kafka"
    filter_normal: bool = False

    @validator('pipeline_connection')
    def name_must_contain_space(cls, v):
        available_connectors = ["zeromq", "kafka"]
        if v not in available_connectors:
            raise ValueError(f'must be one of {available_connectors}')
        return v

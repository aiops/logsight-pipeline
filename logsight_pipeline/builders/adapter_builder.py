from typing import Optional

from logsight.common.patterns.builder import Builder
from logsight.connectors.builders.cls_dict import cls_conn
from logsight.connectors.builders.config_provider import ConnectorConfigProvider
from logsight.connectors.builders.properties import AdapterConfigProperties
from logsight.connectors.serializers import LogBatchSerializer
from logsight.connectors import serializers
from logsight_pipeline.ports.pipeline_adapters import PipelineSourceAdapter


class PipelineAdapterBuilder(Builder):
    def __init__(self, config: Optional[ConnectorConfigProvider] = None):
        self.conn_config = config if config else ConnectorConfigProvider()

    def build(self, config: AdapterConfigProperties) -> PipelineSourceAdapter:
        """
          It takes a connection configuration and returns a Connector object.
          Args:
              config: (ConnectionConfig): Connector configuration object

          Returns:
            Type[ConnectableConnector]: A `Connector` object
      """

        c_name = cls_conn[config.connector.connector_type][config.connector.connection]
        config_cls = self.conn_config.get_config(config.connector.connection)
        if config_cls:
            conn_config = config_cls(**config.connector.params)
            connector = c_name(conn_config)
        else:
            connector = c_name()

        serializer = getattr(serializers, config.serializer)() if config.serializer else LogBatchSerializer()
        return PipelineSourceAdapter(connector, serializer)

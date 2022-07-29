from dacite import from_dict

from logsight_pipeline.configs.properties import ModuleConfigProperties
from logsight.connectors.builders.properties import ConnectorConfigProperties

from logsight.common.patterns.builder import Builder
from logsight.connectors.builders.adapter_builder import AdapterBuilder
from logsight.connectors.builders.connector_builder import ConnectorBuilder
from logsight_pipeline import modules
from logsight_pipeline.modules.core.module import ConnectableModule, Module


class ModuleBuilder(Builder):
    """
    Builder class for building Modules.
    """

    def __init__(self, connection_builder: AdapterBuilder = None):
        self.conn_builder = connection_builder if connection_builder else ConnectorBuilder()

    def build(self, config: ModuleConfigProperties) -> Module:
        """
          It takes a module configuration and returns a module object.
          Args:
              config: (ModuleConfig): Module  configuration object

          Returns:
            Module: A module object
      """
        args = config.args
        c_name = getattr(modules, config.classname)
        if issubclass(c_name, ConnectableModule):
            config.args['connector'] = self.conn_builder.build(
                from_dict(data=config.args['connector'], data_class=ConnectorConfigProperties))
        return c_name(**args)

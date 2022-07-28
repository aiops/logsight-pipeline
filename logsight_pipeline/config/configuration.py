from .properties import PipelineProperties, LogsightPipelineConfigProperties, ModuleConfigProperties


class PipelineConfig:
    def __init__(self):
        self.pipeline = PipelineProperties()
        config = LogsightPipelineConfigProperties()
        if config.filter_normal is True:
            self.pipeline = self._add_filter_module(self.pipeline)

        self.pipeline.connectors.data_source.connector.connection = config.pipeline_connection

    @staticmethod
    def _add_filter_module(pipeline_config):
        filter_normal_config = ModuleConfigProperties(classname="FilterModule", args={
            "key": "metadata.prediction",
            "condition": "equals",
            "value": 1
        }, next_module="risk_score")
        pipeline_config.modules['filter_normal'] = filter_normal_config
        pipeline_config.modules['log_ad'].next_module = "filter_normal"
        return pipeline_config

    def __repr__(self):
        return self.pipeline

    def __getattr__(self, item):
        return getattr(self.pipeline, item)

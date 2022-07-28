import logging

from logsight.analytics_core.logs import LogBatch
from logsight.analytics_core.modules.log_aggregation import LogAggregator
from logsight.common.helpers import to_flat_dict
from .core import TransformModule

logger = logging.getLogger("logsight." + __name__)


class LogAggregationModule(TransformModule):

    def __init__(self):
        super().__init__()
        self.aggregator = LogAggregator()

    def transform(self, data: LogBatch) -> LogBatch:
        data.metadata['agg'] = self.aggregator.aggregate_logs([to_flat_dict(log) for log in data.logs])
        return data

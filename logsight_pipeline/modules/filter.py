import logging

from logsight.analytics_core.logs import LogBatch
from logsight.analytics_core.modules.filter.filter_logs import Filter
from .core import TransformModule

logger = logging.getLogger("logsight." + __name__)


class FilterModule(TransformModule):

    def __init__(self, key: str, condition: str, value: str):
        super().__init__()
        self.log_filter = Filter(key, condition, value)

    def transform(self, data: LogBatch) -> LogBatch:
        data.logs = self.log_filter.filter(data.logs)
        return data

import os
from pathlib import Path

path = Path(os.path.split(os.path.realpath(__file__))[0]) / "logsight_pipeline_config.cfg"
os.environ.setdefault("CONFIG_PATH", str(path))

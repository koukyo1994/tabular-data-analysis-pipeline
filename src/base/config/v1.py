from typing import List
from pathlib import Path

from .baseclass import BaseConfig


class Config(BaseConfig):
    def __init__(self, config: dict):
        super().__init__(config)

        required = {"dataset", "output_dir", "log_dir", "pipeline"}

        keys = set(config.keys())
        missing = required - keys

        if len(missing) > 0:
            self.assertMissingKeys(required, missing)

        self.output_dir = Path(config["output_dir"])
        self.output_dir.mkdir(exist_ok=True, parents=True)

        self.log_dir = Path(config["log_dir"])
        self.log_dir.mkdir(exist_ok=True, parents=True)

        self._pipeline_configs: List[BaseConfig] = []

    def append(self, config: BaseConfig):
        self._pipeline_configs.append(config)


class FeatureConfig(BaseConfig):
    def __init__(self, config: dict):
        super().__init__(config)
        if "feature_name" not in config.keys():
            self.assertMissingKeys({"feature_name"}, {"feature_name"})
        self.feature_name = config["feature_name"]

import pandas as pd

import src.core.callbacks.data as data
import src.utils as utils

from pathlib import Path

from . import SubRunner
from src.core.state import State


class DataRunner(SubRunner):
    signature = "data"

    def __init__(self, config: dict, state: State):
        super().__init__(config, state)

        self.callbacks = [
            data.FileExistenceCheck(),
            data.CheckDataStructure(),
            data.ComputeDataStats()
        ]

    def run(self):
        self._run_callbacks(phase="start")

        for config in self.state.config:
            method, kwargs = data.file_open_method(config)
            columns = data.required_columns(config)
            if columns is not None:
                kwargs["columns"] = columns

            filepath = Path(config["dir"]) / config["name"]

            if self.state.data_stats[str(filepath)] is not None:
                stats_path = self.state.data_stats[str(filepath)]
                stats = data.open_stats(stats_path)

                dtypes = stats["dtypes"]
                if columns is not None:
                    dtypes_cols = {}
                    for col in columns:
                        dtypes_cols[col] = dtypes[col]
                    if method == "read_csv" and config["mode"] == "normal":
                        kwargs["dtype"] = dtypes_cols
                else:
                    kwargs["dtype"] = dtypes

            with utils.timer("Reading " + config["name"], self.state.logger):
                if method in {"read_parquet", "read_pickle", "read_feather"}:
                    df = pd.__getattribute__(method)(filepath, **kwargs)
                    self.state.dataframes[str(filepath)] = df
                elif method == "read_csv":
                    if config["mode"] == "normal":
                        df = pd.__getattribute__(method)(filepath, **kwargs)
                        self.state.dataframes[str(filepath)] = df
                    elif config["mode"] == "large":
                        raise NotImplementedError
                    else:
                        pass
                else:
                    raise NotImplementedError
            self.state.dataframe_roles[str(filepath)] = config["role"]

        self._run_callbacks(phase="end")

import json
import subprocess as sp

import pandas as pd

import src.utils as utils

from pathlib import Path
from typing import Any, Dict, List, Optional

from src.core import State
from src.core.callbacks import Callback, CallbackOrder


# functions
def file_existence(input_dir: Path, filename: str) -> bool:
    return (input_dir / filename).exists()


def file_open_method(config: dict):
    data_format: str = config["name"].split(".")[-1]

    kwargs = {}
    if data_format in {"csv", "tsv"}:
        method = "read_csv"
        if data_format == "tsv":
            kwargs["sep"] = "\t"
    elif data_format == "parquet":
        method = "read_parquet"
    elif data_format in {"pickle", "pkl"}:
        method = "read_pickle"
    elif data_format in {"feather", "ftr"}:
        method = "read_feather"
    else:
        raise NotImplementedError(
            f"Cannot determine file opening method for '{data_format}'")
    return method, kwargs


def open_stats(path: str):
    with open(path, "r") as f:
        stats = json.load(f)

    return stats


def line_count(path: Path) -> int:
    count = int(sp.check_output(["wc", "-l", str(path)]).decode().split()[0])
    return count - 1


def total_size(path: Path) -> int:
    return int(sp.check_output(["ls", "-l", str(path)]).decode().split()[4])


def required_columns(config: dict):
    required = config.get("required")
    if required is None:
        return
    elif required == "all":
        return
    elif isinstance(required, list):
        file_data_format = config["name"].split(".")[-1]
        if file_data_format in {"parquet", "pickle", "pkl"}:
            return
        elif file_data_format in ["csv", "tsv", "ftr", "feather"]:
            return required
    else:
        raise NotImplementedError


def save_stats(df: pd.DataFrame, config: dict):
    stats: Dict[str, Any] = {}

    data_dir = Path(config["dir"])
    data_path = data_dir / config["name"]
    stats_path = data_dir / config["stats"]

    stats["line_count"] = len(df)
    stats["size"] = total_size(data_path)
    stats["dtypes"] = {k: str(v) for k, v in df.dtypes.to_dict().items()}
    stats["nuniques"] = {c: df[c].nunique() for c in df.columns}

    utils.save_json(stats, stats_path)


# on_data_start
class FileExistenceCheck(Callback):
    signature = "data"
    order = CallbackOrder.ASSERTION

    def on_data_start(self, state: State):
        configs: List[Dict[str, Any]] = state.config

        not_exist = []
        stats: Dict[str, Optional[str]] = {}

        for config in configs:
            data_dir = Path(config["dir"])
            filename = config["name"]
            stats_filename = config["stats"]

            filepath = data_dir / filename

            if not file_existence(data_dir, filename):
                not_exist.append(filepath)

            data_format = filename.split(".")[-1]
            if data_format in {"csv", "tsv"}:
                stats[str(filepath)] = str(
                    data_dir / stats_filename) if file_existence(
                        data_dir, stats_filename) else None

        if len(not_exist) > 0:
            msg = "File: [\n"
            for path in not_exist:
                msg += "    " + str(path) + "\n"
            msg += "] does not exist, aborting."
            raise FileNotFoundError(msg)

        state.data_stats.update(stats)


class CheckDataStructure(Callback):
    signature = "data"
    order = CallbackOrder.MIDDLE

    def on_data_loading_start(self, state: State):
        configs = state.config

        target = ""
        id_columns: Dict[str, Optional[str]] = {}
        connect_to: Dict[str, Optional[str]] = {}
        connect_on: Dict[str, Optional[str]] = {}

        for config in configs:
            structure = config["structure"]
            data_dir = Path(config["dir"])
            path = data_dir / config["name"]
            if structure.get("target") is not None:
                target = structure.get("target")
            if structure.get("id_column") is not None:
                id_columns[str(path)] = structure.get("id_column")
            if structure.get("connect_to") is not None:
                connect_to[str(path)] = structure.get("connect_to")
            if structure.get("connect_on") is not None:
                connect_on[str(path)] = structure.get("connect_on")

        state.target_name = target
        state.id_columns = id_columns
        state.connect_to = connect_to
        state.connect_on = connect_on


# on_data_end
class CompressDataFrame(Callback):
    signature = "data"
    order = CallbackOrder.HIGHEST

    def on_data_end(self, state: State):
        with utils.timer("Data Compressing", state.logger):
            dfs = state.dataframes
            for key in dfs:
                dfs[key] = utils.reduce_mem_usage(
                    dfs[key], verbose=True, logger=state.logger)


class ComputeDataStats(Callback):
    signature = "data"
    order = CallbackOrder.LOWER

    def on_data_end(self, state: State):
        configs: List[Dict[str, Any]] = state.config

        for config in configs:
            data_dir = Path(config["dir"])
            stats_path = data_dir / config["stats"]

            mode = config["mode"]
            required = config["required"]
            name = config["name"]

            if not stats_path.exists(
            ) and mode == "normal" and required == "all":
                save_stats(state.dataframes[str(data_dir / name)], config)

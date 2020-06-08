import datetime as dt

import src.core.callbacks as cl
import src.custom as custom
import src.utils as utils

from pathlib import Path
from typing import List, Optional

from src.core.state import State
from src.core.callbacks import Callback


class SubRunner:
    signature = ""
    group = "main"

    def __init__(self, config: dict, state: State):
        self.config = config
        self.state = state
        self.callbacks: List[Callback] = []

    def _run_callbacks(self, phase="start", signature: Optional[str] = None):
        assert phase in {"start", "end"}

        signature = self.signature if signature is None else signature
        method = "on_" + signature + "_" + phase

        # add user defined callbacks
        callbacks_in_group = self.state.callbacks.get(self.group)
        if callbacks_in_group is None:
            user_defined_callbacks = None
        else:
            user_defined_callbacks = self.state.callbacks[self.group].get(
                signature)

        callbacks = self.callbacks
        if user_defined_callbacks is not None:
            preset_callback_names = [
                callback.__class__.__name__ for callback in callbacks
            ]
            for callback in user_defined_callbacks:
                if callback.__class__.__name__ in preset_callback_names:
                    # overwrite
                    index = preset_callback_names.index(
                        callback.__class__.__name__)
                    callbacks[index] = callback
                else:
                    callbacks.append(callback)

        for callback in sorted(callbacks):
            callback._precondition(self.state)
            callback.__getattribute__(method)(self.state)

    def run(self):
        raise NotImplementedError


class Runner:
    def __init__(self, config: dict):
        self.config = config

        log_dir = Path(config["log_dir"])
        log_dir.mkdir(exist_ok=True, parents=True)

        config_name = Path(config["config_path"]).name.replace(".yml", "")
        log_dir = log_dir / config_name
        log_dir.mkdir(parents=True, exist_ok=True)

        self.init_time = dt.datetime.now().strftime("%Y%m%d-%H:%M:%S")
        log_name = self.init_time + ".log"

        logger = utils.get_logger(str(log_dir / log_name))

        self.state = State(config, logger)

    def _prepare_directories(self):
        feature_dir = Path(self.config["feature_dir"])
        output_root_dir = Path(self.config["output_dir"])

        feature_dir.mkdir(exist_ok=True, parents=True)
        output_root_dir.mkdir(exist_ok=True, parents=True)

        self.state.feature_dir = feature_dir

        config_name = self.config["config_path"].split("/")[-1].replace(
            ".yml", "")
        output_dir = (output_root_dir / self.init_time) / config_name

        output_dir.mkdir(parents=True, exist_ok=True)
        self.state.output_dir = output_dir

    def _prepare_callbacks(self):
        all_callbacks = self.config["callbacks"]
        for group in all_callbacks.keys():
            self.state.callbacks[group] = {}

            callbacks_in_group = all_callbacks[group]
            for callback_type in callbacks_in_group:
                self.state.callbacks[group][callback_type] = []
                callbacks = callbacks_in_group[callback_type]

                for callback in callbacks:
                    callback_name = callback["name"]
                    callback_params = {} if callback.get(
                        "params") is None else callback["params"]
                    definetion = callback["definetion"]

                    if "custom" in definetion:
                        submodule = definetion.split(".")[1]
                        instance = custom.__getattribute__(
                            submodule).__getattribute__(
                                "callbacks").__getattribute__(callback_name)(
                                    **callback_params)
                        self.state.callbacks[group][callback_type].append(
                            instance)
                    else:
                        instance = cl.__getattribute__(
                            callback_type).__getattribute__(callback_name)(
                                **callback_params)
                        self.state.callbacks[group][callback_type].append(
                            instance)

    def run(self):
        self._prepare_directories()
        self._prepare_callbacks()

        for pl in self.config["pipeline"]:
            for key, value in pl.items():
                state = State(value, logger=self.state.logger)
                state.callbacks = self.state.callbacks
                state.misc = self.state.misc
                state.output_dir = self.state.output_dir
                state.feature_dir = self.state.feature_dir

                if key == "data":
                    from .data import DataRunner

                    runner = DataRunner(value, state)
                    runner.run()

                    self.state.dataframes = state.dataframes
                    self.state.data_stats = state.data_stats
                    self.state.dataframe_roles = state.dataframe_roles
                    self.state.target_name = state.target_name
                    self.state.id_columns = state.id_columns
                    self.state.connect_to = state.connect_to
                    self.state.connect_on = state.connect_on
                else:
                    pass

                self.state.misc = state.misc

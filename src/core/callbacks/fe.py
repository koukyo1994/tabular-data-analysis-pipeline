import gc

import numpy as np
import pandas as pd

import src.utils as utils

from typing import Optional

from scipy.io import savemat
from scipy.sparse import csr_matrix, hstack

from src.core.state import State
from src.core.callbacks import Callback, CallbackOrder


# on_fe_start
class AssignTarget(Callback):
    signature = "fe"
    order = CallbackOrder.MIDDLE

    def on_fe_end(self, state: State):
        dataframes = state.dataframes
        for key, df in dataframes.items():
            if state.target_name in df.columns:
                state.logger.info(
                    f"Found target `{state.target_name}` in {key}")
                state.target = df[state.target_name].values
                break


# on_fe_end
class SaveFeature(Callback):
    signature = "fe"
    order = CallbackOrder.LOWEST

    def __init__(self, prefix: Optional[str] = None):
        if prefix is None:
            self.prefix = ""
        else:
            self.prefix = prefix + "_"

    def on_fe_end(self, state: State):
        feature_dir = state.feature_dir
        features = state.features

        for name, feature in features.items():
            for phase in ["train", "test"]:
                if isinstance(feature[phase], dict) or isinstance(
                        feature[phase], csr_matrix):
                    mdict = {name: feature[phase]}
                    mat_name = f"{self.prefix}{name}_{phase}.mat"
                    with utils.timer("Saving " + mat_name, state.logger):
                        savemat(feature_dir / mat_name, mdict)
                elif isinstance(feature[phase], pd.DataFrame):
                    ftr_name = f"{self.prefix}{name}_{phase}.ftr"
                    with utils.timer("Saving " + ftr_name, state.logger):
                        for col in feature[phase].columns:
                            if feature[phase][col].dtype == "float16":
                                feature[phase][col] = feature[phase][
                                    col].astype("float32")
                        feature[phase].to_feather(feature_dir / ftr_name)
                else:
                    raise NotImplementedError

        target = state.target
        target_name = f"{self.prefix}main_target.npy"
        with utils.timer("Saving " + target_name, state.logger):
            np.save(feature_dir / target_name, target)


class ConcatenateFeatures(Callback):
    signature = "fe"
    order = CallbackOrder.HIGHEST

    def __init__(self, delete_original=False):
        self.delete_original = delete_original

    def on_fe_end(self, state: State):
        features = state.features

        as_sparse = False
        for feature in features.values():
            if isinstance(feature["train"], dict) or isinstance(
                    feature["train"], csr_matrix):
                as_sparse = True
                break

        main_feature = {}
        with utils.timer("Concatenating `main` features", state.logger):
            if as_sparse:
                for phase in ["train", "test"]:
                    sparse_matrices = []
                    for f in features.values():
                        if isinstance(f[phase], pd.DataFrame):
                            feature_values = csr_matrix(f[phase].values)
                            sparse_matrices.append(feature_values)
                        elif isinstance(f[phase], dict):
                            sparse_dict = f[phase]
                            for sp_mat in sparse_dict.values():
                                sparse_matrices.append(sp_mat)
                        elif isinstance(f[phase], csr_matrix):
                            sparse_matrices.append(f[phase])
                    main_feature[phase] = hstack(sparse_matrices).tocsr()
            else:
                for phase in ["train", "test"]:
                    dfs = []
                    for f in features.values():
                        dfs.append(f[phase])

                    main_feature[phase] = pd.concat(dfs, axis=1)
        state.features["main"] = main_feature

        if self.delete_original:
            keys = list(features.keys())
            keys.remove("main")

            for key in keys:
                del state.features[key]

            gc.collect()


class SortColumns(Callback):
    signature = "fe"
    order = CallbackOrder.MIDDLE

    def on_fe_end(self, state: State):
        features = state.features

        for key in features:
            if isinstance(features[key]["train"], pd.DataFrame):
                with utils.timer(
                        f"Sort columns of features `{key}`",
                        logger=state.logger):
                    features[key]["train"] = features[key]["train"].sort_index(
                        axis=1)
                    if "test" in features[key].keys():
                        features[key]["test"] = features[key][
                            "test"].sort_index(axis=1)

        state.features = features

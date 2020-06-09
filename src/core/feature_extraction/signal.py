import pandas as pd

from typing import List

from tsfresh import extract_features, extract_relevant_features


class TsfreshRelevantTransformer:
    requires_target = True

    def __init__(self, column_id: str, column_sort: str,
                 default_fc_parameters: dict, n_jobs: int):
        self.column_id = column_id
        self.column_sort = column_sort
        self.default_fc_parameters = default_fc_parameters
        self.n_jobs = n_jobs

        self.columns: List[str] = []

    def fit_transform(self, X: pd.DataFrame, y: pd.Series):
        y.index = X[self.column_id].unique()
        features = extract_relevant_features(
            X,
            y,
            column_id=self.column_id,
            column_sort=self.column_sort,
            default_fc_parameters=self.default_fc_parameters,
            n_jobs=self.n_jobs)

        self.columns = features.columns.tolist()

        return features.reset_index(drop=True)

    def transform(self, X: pd.DataFrame):
        features = extract_features(
            X,
            column_id=self.column_id,
            column_sort=self.column_sort,
            default_fc_parameters=self.default_fc_parameters,
            n_jobs=self.n_jobs)
        features = features[self.columns]
        return features.reset_index(drop=True)

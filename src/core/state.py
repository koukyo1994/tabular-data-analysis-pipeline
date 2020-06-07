import logging

import numpy as np
import pandas as pd

from pathlib import Path
from typing import Any, Dict, Optional, Union, Tuple, List

from scipy.sparse import csr_matrix


class State:
    def __init__(self, config: dict, logger: logging.Logger):
        self.config = config

        self.logger = logger

        self.feature_dir = Path("features")
        self.output_dir = Path("output")

        self.dataframes: Dict[str, pd.DataFrame] = {}
        self.dataframe_roles: Dict[str, str] = {}

        self.callbacks: Dict[str, Dict[str, list]] = {}

        self.data_stats: Dict[str, Optional[Union[str, dict]]] = {}

        self.target_name = ""
        self.target: Optional[Union[pd.DataFrame, Union[pd.Series, np.
                                                        ndarray]]] = None
        self.id_columns: Dict[str, Optional[str]] = {}
        self.connect_to: Dict[str, Optional[str]] = {}
        self.connect_on: Dict[str, Optional[str]] = {}

        self.features: Dict[
            str, Dict[str, Union[pd.DataFrame, Dict[str, csr_matrix]]]] = {}
        self.importances: Dict[str, Union[Dict[str, float], pd.DataFrame]] = {}

        self.splits: List[Tuple[np.ndarray, np.ndarray]] = []

        self.models: Dict[str, Dict[str, Any]] = {}
        self.metrics: Dict[str, Dict[str, float]] = {}

        self.predictions: Dict[str, np.ndarray] = {}

        self.misc: Dict[str, Any] = {}

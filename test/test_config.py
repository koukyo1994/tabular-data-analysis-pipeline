import unittest

import yaml

from src.base.config import load_config


class TestLoadConfig(unittest.TestCase):
    def setUp(self):
        with open("test/_config/sample.yml", "r") as f:
            self.sample = dict(yaml.load(f, Loader=yaml.SafeLoader))

    def test_load_config(self):
        config = load_config("config/sample_lgbm_regression.yml")
        self.assertTrue(self._trace_dict(config, self.sample))

    def _trace_dict(self, dict1: dict, dict2: dict):
        is_same = True
        for key in dict1.keys():
            if not is_same:
                return is_same
            if dict2.get(key) is None:
                if dict1.get(key) is not None:
                    return False
            val1 = dict1.get(key)
            val2 = dict2.get(key)
            if isinstance(val1, dict):
                if not isinstance(val2, dict):
                    return False
                else:
                    is_same = self._trace_dict(val1, val2)
            elif isinstance(val1, list):
                if not isinstance(val2, list):
                    return False
                elif len(val1) != len(val2):
                    return False
                else:
                    for i, elem in enumerate(val1):
                        if isinstance(elem, dict):
                            if not isinstance(val2[i], dict):
                                return False
                            else:
                                is_same = self._trace_dict(elem, val2[i])
                        else:
                            if elem != val2[i]:
                                return False
            else:
                if val1 != val2:
                    return False
        return is_same

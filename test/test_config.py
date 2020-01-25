import unittest

import yaml

from src.base.config import load_config


class TestLoadConfig(unittest.TestCase):
    def setUp(self):
        with open("test/_config/sample.yml", "r") as f:
            self.sample = dict(yaml.load(f, Loader=yaml.SafeLoader))

    def test_load_config(self):
        config = load_config("config/sample_lgbm_regression.yml")
        self.assertEqual(config, self.sample)

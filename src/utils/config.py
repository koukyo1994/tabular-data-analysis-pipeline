import yaml

from pathlib import Path
from typing import Any, Dict, Optional, Union


def _get_default() -> dict:
    cfg: Dict[str, Any] = dict()

    cfg["dataset"] = dict()
    cfg["dataset"]["params"] = dict()

    cfg["output_dir"] = "output/"
    cfg["log_dir"] = "log/"

    cfg["pipeline"] = []
    return cfg


def _merge_config(src: Optional[dict], dst: dict):
    if not isinstance(src, dict):
        return

    for k, v in src.items():
        if isinstance(v, dict):
            _merge_config(src[k], dst[k])
        else:
            dst[k] = v


def load_config(cfg_path: Optional[Union[str, Path]] = None,
                require_default=True) -> dict:
    if cfg_path is None:
        if require_default:
            config = _get_default()
        else:
            config = {}
    else:
        with open(cfg_path, "r") as f:
            cfg = dict(yaml.load(f, Loader=yaml.SafeLoader))

        if require_default:
            config = _get_default()
            _merge_config(cfg, config)
        else:
            config = cfg
    return config

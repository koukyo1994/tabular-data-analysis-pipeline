import yaml

from pathlib import Path
from typing import Any, Dict, Optional, Union


def _get_default() -> dict:
    cfg: Dict[str, Any] = dict()
    cfg["version"] = 1

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
            if dst.get(k) is None:
                dst[k] = {}
            _merge_config(src[k], dst[k])
        elif isinstance(v, str):
            if v.endswith(".yml"):
                sub_config = load_config(v, require_default=False)
                _merge_config(sub_config.copy(), sub_config)
                dst[k] = sub_config
            else:
                dst[k] = v
        elif isinstance(v, list):
            if dst.get(k) is None:
                dst[k] = []
            for i, elem in enumerate(v):
                if isinstance(elem, dict):
                    dst[k].append({})
                    _merge_config(elem, dst[k][i])
                elif isinstance(elem, str):
                    if elem.endswith(".yml"):
                        sub_config = load_config(elem, require_default=False)
                        _merge_config(sub_config.copy(), sub_config)
                        dst[k][i] = sub_config
                    else:
                        dst[k].append(elem)
                else:
                    dst[k].append(elem)
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

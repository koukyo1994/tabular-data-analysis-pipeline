import pprint
import yaml

from pathlib import Path
from typing import Any, Dict, Optional, Union


def _get_default() -> dict:
    cfg: Dict[str, Any] = dict()

    cfg["feature_dir"] = "features/"

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
            elif v.startswith("(") and v.endswith(")"):
                dst[k] = eval(v)
            else:
                dst[k] = v
        elif isinstance(v, list):
            if dst.get(k) is None:
                dst[k] = []
            for i, elem in enumerate(v):
                if isinstance(elem, dict):
                    if len(dst[k]) - 1 < i:
                        dst[k] = dst[k].copy()
                        dst[k].append({})
                        _merge_config(elem, dst[k][i])
                elif isinstance(elem, str):
                    if elem.endswith(".yml"):
                        sub_config = load_config(elem, require_default=False)
                        if len(dst[k]) < i + 1:
                            dst[k].append(sub_config)
                        else:
                            dst[k][i] = sub_config
                    elif elem.startswith("(") and elem.endswith(")"):
                        if len(dst[k]) < i + 1:
                            dst[k].append(eval(elem))
                        else:
                            dst[k][i] = eval(elem)
                    else:
                        if len(dst[k]) < i + 1:
                            dst[k].append(elem)
                        else:
                            dst[k][i] = elem
                else:
                    if len(dst[k]) < i + 1:
                        dst[k].append(elem)
                    else:
                        dst[k][i] = elem
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


def _handle_input(input_type="y/n", prompt=""):
    while True:
        if input_type == "y/n":
            yn = input(prompt=prompt)
            if yn.lower() in {"yes", "y"}:
                return True
            elif yn.lower() in {"no", "n"}:
                return False
            else:
                print("Input value must be either `yes` or `no`")
                continue
        elif input_type == "int":
            int_input = input(prompt=prompt)
            try:
                int_result = int(int_input)
            except ValueError:
                print("Input value must be an integer")
                continue
            return int_result
        elif input_type == "str":
            return input(prompt=prompt)
        elif input_type == "float":
            float_input = input(prompt=prompt)
            try:
                float_result = float(float_input)
            except ValueError:
                print("Input value must be a floating point number")
                continue
            return float_result
        elif input_type == "List[str]":
            elements = list()
            elements.append(input(prompt=prompt))
            while True:
                if _handle_input(input_type="y/n", prompt="continue? [y/n]: "):
                    elements.append(_handle_input(input_type="str", prompt=prompt))
                else:
                    break
            return elements
        elif input_type == "List[int]":



def _collect_config_information(base_config: dict, show_current_value=False):
    config = {}
    for key, value in base_config.items():
        if isinstance(value, dict):
            if show_current_value:
                print("Current:")
                pprint.pprint(value)
                print("Do you want to change? [y/n]: ", end="")
                yn = input()
            config[key] = _collect_config_information(value)
        elif value == "str":



def generate_config(config_type: str):
    print("Base config:", end="")
    base = input()

    if base == "template":
        base_config = load_config(f"configs/{config_type}/template.yml")
    else:
        base_config = load_config(base)


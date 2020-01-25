import v1


def parse_config(config: dict):
    version = config["version"]
    if version == 1:
        config_wrapper = v1.Config(config)
        return config_wrapper
    else:
        raise NotImplementedError(
            f"version {version} for config hasn't been defined yet")

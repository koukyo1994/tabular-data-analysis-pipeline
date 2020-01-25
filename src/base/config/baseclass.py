class BaseConfig(object):
    def __init__(self, config: dict):
        if "version" not in config.keys():
            raise AttributeError("config must have attribute 'version'")
        self.version = config["version"]
        self.raw_config = config

    def assertMissingKeys(self, required: set, missing: set):
        raise AttributeError(
            "Version {} config requires keys - {}, missing - {}".format(
                self.version, required, missing))

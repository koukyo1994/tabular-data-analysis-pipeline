import src.utils as utils

from src.core import load_config
from src.core import Runner

if __name__ == "__main__":
    args = utils.get_parser().parse_args()
    config = load_config(args.config)

    config["config_path"] = args.config

    runner = Runner(config)
    runner.run()

from src.base.config import load_config
from src.utils import get_parser

if __name__ == "__main__":
    args = get_parser().parse_args()
    config = load_config(args.config)
    import pdb
    pdb.set_trace()

import argparse


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser_run = subparsers.add_parser("run", help="Run config")
    parser_run.add_argument(
        "--config", required=True, help="path to config file")

    parser_generate = subparsers.add_parser("generate", help="Generate config")
    parser_generate.add_argument(
        "--type", nargs="*", required=True, help="type of config")
    return parser

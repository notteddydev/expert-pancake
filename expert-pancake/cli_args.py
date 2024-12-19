import argparse
import os
from pathlib import Path


def exit_if_args_invalid(cli_args):
    """
    
    """
    must_exist_dirs = ["destination", "origin"]
    if cli_args.copydestination is not None:
        must_exist_dirs.append("copydestination")

    for args_attr in must_exist_dirs:
        if not os.path.isdir(getattr(cli_args, args_attr)):
            print(f"{args_attr.capitalize()} directory does not exist. Exiting.")
            exit()

    if not os.listdir(cli_args.origin):
        print("Origin empty. Exiting.")
        exit()


def get_args(docstring=None):
    """
    
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-d", "--destination",
                        help="The directory to move files to.",
                        required=True,
                        type=Path,
                        )
    parser.add_argument("-c", "--copydestination",
                        default=None,
                        help="The directory to save copies to.",
                        required=False,
                        type=Path,
                        )
    parser.add_argument("-o", "--origin",
                        help="The directory to move files from.",
                        required=True,
                        type=Path,
                        )
    parser.add_argument("-v", "--verbose",
                        action="store_const",
                        const=True,
                        default=False,
                        help="Add this for more chit-chat.",
                        )
    return parser.parse_args()

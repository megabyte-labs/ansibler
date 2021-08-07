from ansibler.args.cmd import ARGS


def display_help() -> None:
    """
    Displays some info about the parameters
    """
    args_str = "\n".join([
        f"\t--{arg.get('arg_name')}: {arg.get('arg_help')}"
        for arg in ARGS
    ])
    print(f"You must pass any of the following arguments:\n{args_str}")

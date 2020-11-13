def argparse(possible: list, text: str):
    possible = [f"--{p}" for p in possible]
    args = []
    for arg in possible:
        if arg in text:
            text = text.replace(arg, "")
            args.append(arg.replace("--", ""))
    return args, text

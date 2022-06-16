import re
import shlex

from io import StringIO
from typing import Dict, Tuple
from argparse import ArgumentParser

FLAG_REGEX = re.compile(r"-\w+")


class Flag:
    def __init__(self, prefix, help, action=None, nargs=None, default="dummy_default"):
        self.args = (prefix,)
        self.kwargs = {"help": help}
        if action:
            self.kwargs["action"] = action
        if nargs:
            self.kwargs["nargs"] = nargs
        if default != "dummy_default":
            self.kwargs["default"] = default


class ParseError(Exception):
    def __init__(self, message):
        self.message = message


class ArgumentParser(ArgumentParser):
    def error(self, message):
        raise ParseError(message)


class FlagParser:
    def __init__(self, flags, desc):
        self.parser = ArgumentParser(add_help=False, description=desc)
        for flag in flags:
            self.parser.add_argument(*flag.args, **flag.kwargs)
        self.parser.add_argument("-h", "--help", help="Display this message.", action="store_true")

    def parse(self, text, known=False):
        text = shlex.split(text)
        return self.parser.parse_known_args(text) if known else self.parser.parse_args(text)

    def get_help(self):
        string = StringIO()
        self.parser.print_help(string)
        return string.getvalue()


def seprate_flags(message: str) -> str:
    return FLAG_REGEX.sub("", message)

def parse_range(numbers: str, max=100):
    for x in numbers.split(','):
        x = x.strip()
        if x.isdigit():
            yield int(x)
        elif x[0] == '<':
            yield from range(int(x[1:])-1, 0, -1)
        elif x[0] == ">":
            yield from range(int(x[1:])+1, max)
        elif '-' in x:
            xr = x.split('-')
            yield from range(int(xr[0].strip()), int(xr[1].strip())+1)
        else:
            raise ValueError(f"Unknown range specified: {x}")

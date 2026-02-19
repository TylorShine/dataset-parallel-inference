import ast
from os import environ
from os.path import basename
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

load_dotenv(Path(__file__).parent.joinpath(".env"))

paths = Path(__file__).parent.joinpath("functions").glob("*.py")

oai = OpenAI()


class ArgList(BaseModel):
    args: list[str]


for path in paths:
    print(ast.parse(path.read_text()).body[0].name)
    for _item in ast.parse(path.read_text()).body[0].body:
        if isinstance(_item, ast.FunctionDef):
            if _item.name == "build_description":
                args = [a.arg for a in _item.args.args]
                args.remove("self")
                print(args)

import json
import subprocess
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from loguru import logger


@dataclass
class Argument:
    name: str
    default: Optional[str] = None
    value: Optional[str] = None


@dataclass
class Recipe:
    name: str
    doc: str
    arguments: List[Argument]
    body: List[List[str]]


def get_just_schema() -> Dict[str, Any]:
    """Runs `just --dump --dump-format json` and returns the parsed JSON."""
    try:
        result = subprocess.run(
            ["just", "--dump", "--dump-format", "json"],
            capture_output=True,
            text=True,
            check=True,
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        logger.error("Error running just: {}", e)
        return {}
    except FileNotFoundError:
        logger.error("Error: 'just' command not found.")
        return {}


def parse_recipes(schema: Dict[str, Any]) -> List[Recipe]:
    """Parses the raw JSON schema into a list of Recipe objects."""
    recipes: List[Recipe] = []

    raw_recipes = schema.get("recipes", {})

    for name, data in raw_recipes.items():
        doc = data.get("doc", "")
        if doc is None:
            doc = ""
        doc = doc.strip()

        args = []
        for arg_data in data.get("parameters", []):
            arg_name = arg_data.get("name")
            arg_default = arg_data.get("default")
            args.append(Argument(name=arg_name, default=arg_default))

        raw_body = data.get("body", [])
        simple_body = []
        for line_items in raw_body:
            line_str = ""
            for item in line_items:
                if isinstance(item, str):
                    line_str += item
                elif isinstance(item, dict) and "text" in item:
                    line_str += item["text"]

                elif isinstance(item, dict) and "variable" in item:
                    line_str += f"{{{{{item['variable']}}}}}"
                elif isinstance(item, list):
                    # Handle nested tokens like [['variable', 'env']] or general list of tokens
                    for subitem in item:
                        if (
                            isinstance(subitem, list)
                            and len(subitem) == 2
                            and subitem[0] == "variable"
                        ):
                            line_str += f"{{{{{subitem[1]}}}}}"
                        elif isinstance(subitem, str):
                            line_str += subitem
            simple_body.append([line_str])

        recipes.append(Recipe(name=name, doc=doc, arguments=args, body=simple_body))

    return recipes

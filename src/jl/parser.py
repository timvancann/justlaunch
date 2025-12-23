import json
import subprocess
from dataclasses import dataclass
from typing import List, Optional, Dict, Any


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
        # Fallback or empty dict if just is not found or fails
        print(f"Error running just: {e}")
        return {}
    except FileNotFoundError:
        print("Error: 'just' command not found.")
        return {}


def parse_recipes(schema: Dict[str, Any]) -> List[Recipe]:
    """Parses the raw JSON schema into a list of Recipe objects."""
    recipes: List[Recipe] = []

    raw_recipes = schema.get("recipes", {})

    for name, data in raw_recipes.items():
        # Clean up docstring: take first line, strip whitespace
        doc = data.get("doc", "")
        if doc is None:
            doc = ""
        doc = doc.strip()

        # Parse arguments
        args = []
        for arg_data in data.get("parameters", []):
            arg_name = arg_data.get("name")
            arg_default = arg_data.get("default")
            args.append(Argument(name=arg_name, default=arg_default))

        # Body - extracted as list of commands
        # Note: just dump format for body is a bit complex, usually a list of list of items
        # where items can be strings or evaluation structures.
        # For simple purpose we grab the 'body' if simple.
        # Deep inspection of structure needed for full fidelity but MVP simply stores raw if possible
        # checking structure: "body": [ [ { "kind": "Text", "text": "echo hello" } ] ]

        # For now, let's just store the full raw body structure or simplify it.
        # Let's simplify to list of command strings for display.
        raw_body = data.get("body", [])
        simple_body = []
        for line_items in raw_body:
            line_str = ""
            for item in line_items:
                if isinstance(item, str):
                    line_str += item
                elif isinstance(item, dict) and "text" in item:
                    line_str += item["text"]
                # Just has other types like 'Variable', 'Evaluate', etc.
                # For MVP let's do a best effort text reconstruction
                elif isinstance(item, dict) and "variable" in item:
                    line_str += f"{{{{{item['variable']}}}}}"
            simple_body.append([line_str])

        recipes.append(Recipe(name=name, doc=doc, arguments=args, body=simple_body))

    return recipes

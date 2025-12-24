from unittest.mock import patch, MagicMock
from jl.parser import get_just_schema, parse_recipes
import subprocess
import json
import os


def test_parse_recipes():
    cwd = os.path.dirname(__file__)
    justfile_path = os.path.join(cwd, "justfile.test")

    try:
        result = subprocess.run(
            ["just", "--justfile", justfile_path, "--dump", "--dump-format", "json"],
            capture_output=True,
            text=True,
            check=True,
        )
        schema = json.loads(result.stdout)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        import pytest

        pytest.fail(f"Failed to dump justfile: {e}")

    recipes = parse_recipes(schema)

    assert len(recipes) == 2

    build = next(r for r in recipes if r.name == "build")
    assert build.doc == "Build the project"
    assert len(build.arguments) == 0
    assert build.body == [["uv build"]]

    deploy = next(r for r in recipes if r.name == "deploy")
    assert deploy.doc == "Deploy to a specific environment"
    assert len(deploy.arguments) == 1
    assert deploy.arguments[0].name == "env"

    assert 'echo "Deploying to {{env}}"' in deploy.body[0][0]


@patch("jl.parser.subprocess.run")
def test_get_just_schema_success(mock_run):
    fake_json = '{"recipes": {"test": {"name": "test", "doc": "doc", "body": [], "arguments": []}}}'
    mock_run.return_value = MagicMock(stdout=fake_json, returncode=0)

    schema = get_just_schema()
    assert "recipes" in schema
    assert "test" in schema["recipes"]


@patch("jl.parser.subprocess.run")
def test_get_just_schema_failure(mock_run):
    mock_run.side_effect = FileNotFoundError
    schema = get_just_schema()
    assert schema == {}

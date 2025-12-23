from unittest.mock import patch, MagicMock
from jl.parser import get_just_schema, parse_recipes

SAMPLE_JSON_OUTPUT = """
{
  "recipes": {
    "build": {
      "attributes": [],
      "body": [
        [
          {
            "text": "uv build",
            "kind": "Text"
          }
        ]
      ],
      "dependencies": [],
      "doc": "Build the project",
      "file_depth": 0,
      "kind": "default",
      "lineno": 11,
      "name": "build",
      "parameters": [],
      "priors": 0,
      "private": false,
      "quiet": false,
      "shebang": false
    },
    "deploy": {
      "attributes": [],
      "body": [
        [
          {
             "text": "echo \\"Deploying to ",
             "kind": "Text"
          },
          {
             "variable": "env",
             "kind": "Variable"
          },
          {
             "text": "\\"",
             "kind": "Text"
          }
        ]
      ],
      "dependencies": [],
      "doc": "Deploy to a specific environment",
      "file_depth": 0,
      "kind": "default",
      "lineno": 15,
      "name": "deploy",
      "parameters": [
        {
          "export": false,
          "kind": "singular",
          "name": "env"
        }
      ],
      "priors": 0,
      "private": false,
      "quiet": false,
      "shebang": false
    }
  }
}
"""


def test_parse_recipes():
    import json

    schema = json.loads(SAMPLE_JSON_OUTPUT)
    recipes = parse_recipes(schema)

    assert len(recipes) == 2

    # Check 'build' recipe
    build = next(r for r in recipes if r.name == "build")
    assert build.doc == "Build the project"
    assert len(build.arguments) == 0
    assert build.body == [["uv build"]]

    # Check 'deploy' recipe
    deploy = next(r for r in recipes if r.name == "deploy")
    assert deploy.doc == "Deploy to a specific environment"
    assert len(deploy.arguments) == 1
    assert deploy.arguments[0].name == "env"
    # Note: Our simple body parser might construct it slightly differently depending on implementation
    # Let's check what we expect from the implementation:
    # line_str += item["text"] or {{variable}}
    # So: "echo \"Deploying to " + "{{env}}" + "\""
    expected_body_line = 'echo "Deploying to {{env}}"'
    assert deploy.body[0][0] == expected_body_line


@patch("jl.parser.subprocess.run")
def test_get_just_schema_success(mock_run):
    mock_run.return_value = MagicMock(stdout=SAMPLE_JSON_OUTPUT, returncode=0)

    schema = get_just_schema()
    assert "recipes" in schema
    assert "build" in schema["recipes"]


@patch("jl.parser.subprocess.run")
def test_get_just_schema_failure(mock_run):
    mock_run.side_effect = FileNotFoundError
    schema = get_just_schema()
    assert schema == {}

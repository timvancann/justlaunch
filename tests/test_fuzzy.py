from jl.tui import fuzzy_match
from jl.parser import Recipe


def test_fuzzy_match_requirement():
    """
    User requirement: 'rn' should find 'run'.
    This test asserts the desired behavior.
    """
    recipe = Recipe(name="run", doc="Execute the project", arguments=[], body=[])

    query = "rn"

    is_match = fuzzy_match(query, recipe.name)

    assert is_match, "Expected 'rn' to fuzzy match 'run'"

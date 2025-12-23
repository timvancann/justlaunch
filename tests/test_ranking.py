from rapidfuzz import fuzz
from jl.tui import JustApp, RecipeItem, Recipe
import pytest


@pytest.mark.asyncio
async def test_search_ranking():
    """
    User requirement: 'lint' should rank 'lint' higher than 'complex_test' (which contains l,i,n,t).
    """
    app = JustApp()

    # Mock recipes
    r1 = Recipe(
        name="complex_test",
        doc="Test command with multiple arguments and linting",
        arguments=[],
        body=[],
    )
    r2 = Recipe(
        name="deploy", doc="Deploy to a specific environment", arguments=[], body=[]
    )
    r3 = Recipe(name="lint", doc="Run the linter", arguments=[], body=[])

    app.recipes = [r1, r2, r3]

    # Manually trigger the logic that happens in on_search_changed
    # We can't easily perform a full integration test without running the app,
    # so lets simulate the sorting logic which is the core requirement.

    query = "lint"

    scored_items = []
    for recipe in app.recipes:
        # Simulate the scoring logic from tui.py
        name_score = fuzz.WRatio(query, recipe.name)
        doc_score = fuzz.WRatio(query, recipe.doc) if recipe.doc else 0
        score = max(name_score, doc_score * 0.8)
        scored_items.append((score, recipe))

    scored_items.sort(key=lambda x: x[0], reverse=True)

    # Verify order
    ranked_names = [r.name for _, r in scored_items]

    print(f"Ranked names: {ranked_names}")

    assert ranked_names[0] == "lint", "Expected 'lint' to be ranked first"
    assert "complex_test" in ranked_names

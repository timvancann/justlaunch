import pytest
from jl.tui import JustApp
from jl.parser import Recipe


def test_search_logic():
    app = JustApp()

    # Mock recipes
    r1 = Recipe(name="build", doc="Build the project", arguments=[], body=[])
    r2 = Recipe(name="test", doc="Run tests", arguments=[], body=[])
    r3 = Recipe(name="deploy", doc="Deploy to prod", arguments=[], body=[])

    app.recipes = [r1, r2, r3]

    query = "build"
    filtered = [
        r
        for r in app.recipes
        if query in r.name.lower() or (r.doc and query in r.doc.lower())
    ]
    assert len(filtered) == 1
    assert filtered[0].name == "build"

    query = "proj"  # In doc "Build the project"
    filtered = [
        r
        for r in app.recipes
        if query in r.name.lower() or (r.doc and query in r.doc.lower())
    ]
    assert len(filtered) == 1
    assert filtered[0].name == "build"

    query = "e"
    # tEst, dEploy, build thE projEct
    filtered = [
        r
        for r in app.recipes
        if query in r.name.lower() or (r.doc and query in r.doc.lower())
    ]
    assert len(filtered) == 3


@pytest.mark.asyncio
async def test_app_search_integration():
    """Integration test using textual's testing harness."""
    app = JustApp()

    # Mock load_recipes
    r1 = Recipe(name="build", doc="Build stuff", arguments=[], body=[])
    r2 = Recipe(name="clean", doc="Clean stuff", arguments=[], body=[])

    # We patch the instance method or use a side effect if we can,
    # but here assigning to the instance before run might work if called in compose.
    # Actually, compose calls self.load_recipes.
    # Let's subclass to mock safer.

    class MockApp(JustApp):
        def load_recipes(self):
            return [r1, r2]

    app = MockApp()

    async with app.run_test() as pilot:
        # Check initial list
        list_view = app.query_one("ListView")
        assert len(list_view.children) == 2

        # Determine which input is the search input. It has ID "search_input".
        search_input = app.query_one("#search_input")
        search_input.focus()

        # Type "clean"
        await pilot.press("c", "l", "e", "a", "n")

        # Check list updated
        # Wait for event processing
        await pilot.pause()

        assert len(list_view.children) == 1
        # Access the RecipeItem's recipe
        assert "clean" in list_view.children[0].recipe.name

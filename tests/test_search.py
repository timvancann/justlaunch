import pytest
from jl.tui import JustApp
from jl.parser import Recipe


def test_search_logic():
    app = JustApp()

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

    query = "proj"
    filtered = [
        r
        for r in app.recipes
        if query in r.name.lower() or (r.doc and query in r.doc.lower())
    ]
    assert len(filtered) == 1
    assert filtered[0].name == "build"

    query = "e"

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

    r1 = Recipe(name="build", doc="Build stuff", arguments=[], body=[])
    r2 = Recipe(name="clean", doc="Clean stuff", arguments=[], body=[])

    class MockApp(JustApp):
        def load_recipes(self):
            return [r1, r2]

    app = MockApp()

    async with app.run_test() as pilot:
        list_view = app.query_one("ListView")
        assert len(list_view.children) == 2

        search_input = app.query_one("#search_input")
        search_input.focus()

        await pilot.press("c", "l", "e", "a", "n")

        await pilot.pause()

        assert len(list_view.children) == 1

        assert "clean" in list_view.children[0].recipe.name

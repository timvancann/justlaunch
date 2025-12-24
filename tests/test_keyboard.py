import pytest
from jl.tui import JustApp
from jl.parser import Recipe


@pytest.mark.asyncio
async def test_app_search_navigation():
    """Test keyboard navigation from search input."""

    r1 = Recipe(name="build", doc="Build", arguments=[], body=[])
    r2 = Recipe(name="test", doc="Test", arguments=[], body=[])

    class MockApp(JustApp):
        def load_recipes(self):
            return [r1, r2]

    app = MockApp()

    async with app.run_test() as pilot:
        await pilot.click("#search_input")

        list_view = app.query_one("ListView")
        assert list_view.index == 0 or list_view.index is None

        await pilot.press("ctrl+j")
        assert list_view.index == 1

        await pilot.press("ctrl+k")
        assert list_view.index == 0

        await pilot.press("tab")
        assert list_view.index == 1

        await pilot.press("down")

        assert list_view.index == 1

        await pilot.press("up")
        assert list_view.index == 0


@pytest.mark.asyncio
async def test_search_filtering_resets_index():
    """Test that searching resets selection to top."""
    r1 = Recipe(name="apple", doc="", arguments=[], body=[])
    r2 = Recipe(name="banana", doc="", arguments=[], body=[])

    class MockApp(JustApp):
        def load_recipes(self):
            return [r1, r2]

    app = MockApp()
    async with app.run_test() as pilot:
        list_view = app.query_one("ListView")
        await pilot.click("#search_input")

        await pilot.press("down")
        assert list_view.index == 1

        await pilot.press("a", "p", "p")
        await pilot.pause()

        assert len(list_view.children) == 1
        assert list_view.index == 0
        assert "apple" in list_view.children[0].recipe.name

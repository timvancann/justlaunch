import pytest
from jl.tui import JustApp
from jl.parser import Recipe


@pytest.mark.asyncio
async def test_app_search_navigation():
    """Test keyboard navigation from search input."""

    # Mock recipes
    r1 = Recipe(name="build", doc="Build", arguments=[], body=[])
    r2 = Recipe(name="test", doc="Test", arguments=[], body=[])

    class MockApp(JustApp):
        def load_recipes(self):
            return [r1, r2]

    app = MockApp()

    async with app.run_test() as pilot:
        # Initial focus should be on search input (or we focus it)
        # Actually compose order puts it first in focus chain usually? Input is focusable.
        # Let's ensure focus.
        await pilot.click("#search_input")

        list_view = app.query_one("ListView")
        assert list_view.index == 0 or list_view.index is None

        # Test Cycle Down (Ctrl+j)
        await pilot.press("ctrl+j")
        assert list_view.index == 1

        # Test Cycle Up (Ctrl+k)
        await pilot.press("ctrl+k")
        assert list_view.index == 0

        # Test Tab cycle (Down)
        await pilot.press("tab")
        assert list_view.index == 1

        # Test Arrow Down from Input (Custom handling)
        await pilot.press("down")
        # Should loop or stay at bottom? ListView behavior. 2 items, index 1 is last.
        # Calling cursor_down on last item usually does nothing
        assert list_view.index == 1

        # Let's go up
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

        # Go down to banana
        await pilot.press("down")
        assert list_view.index == 1

        # Type "app"
        await pilot.press("a", "p", "p")
        await pilot.pause()

        # Should be filtered to apple and index 0
        assert len(list_view.children) == 1
        assert list_view.index == 0
        assert "apple" in list_view.children[0].recipe.name

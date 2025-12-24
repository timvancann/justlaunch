from textual.app import App, ComposeResult
import sys
import os
from textual.widgets import (
    Footer,
    ListView,
    ListItem,
    Label,
    Static,
    Input,
    RichLog,
)
from textual.containers import Horizontal, Vertical
from textual import on, events, work
from textual.binding import Binding
from pathlib import Path
from jl.parser import get_just_schema, parse_recipes, Recipe
from jl.runner import JustRunner
from jl.cache import ArgumentCache
from jl.forms import ArgumentForm
from loguru import logger
from rich.text import Text

logger.remove()
logger.add("jl.log", level="INFO")

try:
    from rapidfuzz import fuzz
except ImportError:
    fuzz = None


def fuzzy_match(query: str, text: str) -> bool:
    """Returns True if query is a subsequence of text (case-insensitive)."""

    if not query:
        return True

    query = query.lower()
    text = text.lower()

    if query in text:
        return True

    q_len = len(query)
    t_len = len(text)

    if q_len > t_len:
        return False

    t_idx = 0
    q_idx = 0

    while t_idx < t_len and q_idx < q_len:
        if text[t_idx] == query[q_idx]:
            q_idx += 1
        t_idx += 1

    return q_idx == q_len


class RecipeItem(ListItem):
    """A ListItem that holds a Recipe."""

    def __init__(self, recipe: Recipe) -> None:
        self.recipe = recipe
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Label(f"[bold]{self.recipe.name}[/bold]")
        if self.recipe.doc:
            yield Label(f"[dim]{self.recipe.doc}[/dim]")


class RecipeListView(ListView):
    """List of available recipes."""

    BINDINGS = [
        Binding("ctrl+j", "cursor_down", "Down", show=True),
        Binding("ctrl+k", "cursor_up", "Up", show=True),
        Binding("enter", "select", "Select"),
    ]

    def clear(self) -> None:
        logger.info("RecipeListView.clear() called")
        super().clear()


class SearchInput(Input):
    """Input widget that handles navigation keys for the command list."""

    def key_down(self, event: events.Key) -> None:
        self.app.action_list_cursor_down()
        event.stop()

    def key_up(self, event: events.Key) -> None:
        self.app.action_list_cursor_up()
        event.stop()

    def key_ctrl_j(self, event: events.Key) -> None:
        self.app.action_list_cursor_down()
        event.stop()

    def key_ctrl_k(self, event: events.Key) -> None:
        self.app.action_list_cursor_up()
        event.stop()

    def key_tab(self, event: events.Key) -> None:
        self.app.action_list_cursor_down()
        event.stop()

    def key_enter(self, event: events.Key) -> None:
        pass

    def key_alt_d(self, event: events.Key) -> None:
        self.app.action_scroll_details_down()
        event.stop()

    def key_alt_u(self, event: events.Key) -> None:
        self.app.action_scroll_details_up()
        event.stop()

    def key_ctrl_d(self, event: events.Key) -> None:
        self.app.action_scroll_log_down()
        event.stop()

    def key_ctrl_u(self, event: events.Key) -> None:
        self.app.action_scroll_log_up()
        event.stop()


class JustApp(App):
    """A TUI for JustLaunch."""

    CSS_PATH = Path(__file__).parent / "app.tcss"

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("/", "focus_search", "Search"),
        ("alt+d", "scroll_details_down", "Body ↓"),
        ("alt+u", "scroll_details_up", "Body ↑"),
        ("ctrl+d", "scroll_log_down", "Log ↓"),
        ("ctrl+u", "scroll_log_up", "Log ↑"),
        ("ctrl+j", "list_cursor_down", "Next"),
        ("ctrl+k", "list_cursor_up", "Prev"),
    ]

    def __init__(self):
        super().__init__()
        self.theme = "dracula"
        self.recipes = []

        start_dir = os.getcwd()
        self.justfile_path = os.path.join(start_dir, "justfile")
        self.arg_cache = ArgumentCache()

    def load_recipes(self):
        schema = get_just_schema()
        if not schema:
            return []
        return parse_recipes(schema)

    def action_focus_search(self):
        self.query_one("#search_input").focus()

    def action_list_cursor_down(self):
        """Move cursor down in the command list."""
        command_list = self.query_one("#command_list", RecipeListView)
        if command_list.index is not None:
            command_list.action_cursor_down()
        else:
            command_list.index = 0

    def action_list_cursor_up(self):
        """Move cursor up in the command list."""
        command_list = self.query_one("#command_list", RecipeListView)
        if command_list.index is not None:
            command_list.action_cursor_up()

    def action_scroll_details_down(self):
        """Scroll details view down."""
        details = self.query_one("#details", Static)
        details.scroll_down()

    def action_scroll_details_up(self):
        """Scroll details view up."""
        details = self.query_one("#details", Static)
        details.scroll_up()

    def action_scroll_log_down(self):
        """Scroll log view down."""
        log = self.query_one("#log", RichLog)

        log.scroll_page_down()

    def action_scroll_log_up(self):
        """Scroll log view up."""
        log = self.query_one("#log", RichLog)
        log.scroll_page_up()

    def compose(self) -> ComposeResult:
        self.recipes = self.load_recipes()

        with Horizontal():
            with Vertical(id="sidebar"):
                yield Label("[bold]Recipes[/bold]", classes="sidebar-header")
                yield SearchInput(placeholder="Search...", id="search_input")

                recipe_items = [RecipeItem(r) for r in self.recipes]
                # logger.info(recipe_items)
                yield RecipeListView(*recipe_items, id="command_list")

            with Vertical(id="main_content"):
                yield Static("Select a recipe to see details.", id="details")
                yield RichLog(id="log", highlight=True, markup=True)

        yield Footer()

    @on(Input.Changed, "#search_input")
    def on_search_changed(self, event: Input.Changed):
        # Strict check to ensure we only respond to search input
        if event.input.id != "search_input":
            return

        query = event.value.lower()
        command_list = self.query_one("#command_list", RecipeListView)

        command_list.clear()

        scored_items = []
        for recipe in self.recipes:
            name_match = fuzzy_match(query, recipe.name)
            doc_match = recipe.doc and fuzzy_match(query, recipe.doc)

            if name_match or doc_match:
                score = 0
                if fuzz:
                    name_score = fuzz.WRatio(query, recipe.name)
                    doc_score = fuzz.WRatio(query, recipe.doc) if recipe.doc else 0

                    score = max(name_score, doc_score * 0.8)

                scored_items.append((score, recipe))

        scored_items.sort(key=lambda x: x[0], reverse=True)

        for _, recipe in scored_items:
            command_list.append(RecipeItem(recipe))

        if len(command_list.children) > 0:
            command_list.index = 0

        logger.info(f"Search query: '{query}', matches: {len(scored_items)}")

    @on(Input.Changed)
    def on_any_input_changed(self, event: Input.Changed):
        logger.info(
            f"Input changed from widget ID: {event.input.id}, value: '{event.value}'"
        )

    @on(ListView.Selected)
    def on_recipe_selected(self, event: ListView.Selected):
        self.update_details(event.item)

    @on(ListView.Highlighted)
    def on_recipe_highlighted(self, event: ListView.Highlighted):
        self.update_details(event.item)

    def update_details(self, item):
        if isinstance(item, RecipeItem):
            recipe = item.recipe
            details = self.query_one("#details", Static)

            content = f"[bold underline]Recipe:[/bold underline] {recipe.name}\n\n"
            if recipe.doc:
                content += f"[italic]{recipe.doc}[/italic]\n\n"

            if recipe.arguments:
                content += "[bold]Arguments:[/bold]\n"
                for arg in recipe.arguments:
                    default = f" (default: {arg.default})" if arg.default else ""
                    content += f"- {arg.name}{default}\n"
                content += "\n"

            content += "[bold]Body:[/bold]\n"
            for line in recipe.body:
                content += f"{line[0]}\n"

            details.update(content)

    @on(Input.Submitted, "#search_input")
    def on_search_submitted(self, event: Input.Submitted):
        command_list = self.query_one("#command_list", RecipeListView)
        if command_list.highlighted_child:
            self.initiate_run(command_list.highlighted_child.recipe)

    def initiate_run(self, recipe: Recipe):
        if recipe.arguments:

            def handler(result):
                if result and not result.cancelled:
                    args_list = []
                    for arg in recipe.arguments:
                        val = result.arguments.get(arg.name)
                        if val is not None:
                            args_list.append(val)
                    self.run_recipe_with_args(recipe, args_list)

            self.push_screen(
                ArgumentForm(recipe, self.arg_cache, self.justfile_path), handler
            )
        else:
            self.run_recipe_with_args(recipe, [])

    @work(exclusive=True, thread=False)
    async def run_recipe_with_args(self, recipe: Recipe, args: list[str]):
        log = self.query_one("#log", RichLog)

        if recipe.is_interactive:
            # For interactive recipes, we suspend the app and run the command directly
            # in the terminal so the user can interact with it.
            with self.suspend():
                cmd = ["just", recipe.name]
                if args:
                    cmd.extend(args)
                # Use subprocess.call to block until finished
                # We need to import subprocess
                import subprocess

                subprocess.call(cmd)
            # After returning, maybe log that it finished?
            log.write(
                f"\n[bold yellow]Interactive recipe {recipe.name} finished.[/bold yellow]"
            )
            return

        log.clear()

        log.write(f"\n[bold blue]Running {recipe.name}...[/bold blue]")

        async for line in JustRunner.run_recipe(recipe.name, args):
            log.write(Text.from_ansi(line))


def run():
    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        try:
            from textual_serve.server import Server
        except ImportError:
            logger.error(
                "textual-serve is required for the 'serve' command. Please install it."
            )
            sys.exit(1)

        server = Server(command="jl")
        server.serve()
    else:
        app = JustApp()
        app.run()


if __name__ == "__main__":
    run()

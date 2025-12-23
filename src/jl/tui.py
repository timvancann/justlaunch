from textual.app import App, ComposeResult
from textual.widgets import (
    Header,
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
from jl.parser import get_just_schema, parse_recipes, Recipe
from jl.runner import JustRunner
from jl.cache import ArgumentCache
from jl.forms import ArgumentForm
import os


class RecipeItem(ListItem):
    """A ListItem that holds a Recipe."""

    def __init__(self, recipe: Recipe) -> None:
        self.recipe = recipe
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Label(f"[bold]{self.recipe.name}[/bold]")
        if self.recipe.doc:
            yield Label(f"[dim]{self.recipe.doc}[/dim]")


class CommandList(ListView):
    """List of available recipes."""

    BINDINGS = [
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
        Binding("enter", "select", "Select"),
    ]


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
        # Cycle down on tab
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

    CSS = """
    Screen {
        layout: horizontal;
    }
    
    #sidebar {
        width: 30%;
        height: 100%;
        border-right: solid $primary;
    }
    
    #search_input {
        dock: top;
        margin: 1 1 0 1;
    }
    
    #env_select {
        dock: top;
        margin: 1;
    }

    #command_list {
         height: 1fr; 
         overflow-y: auto;
    }
    
    #main_content {
        width: 70%;
        height: 100%;
        padding: 1;
        layout: vertical;
    }
    
    #details {
        height: 40%;
        border-bottom: solid $secondary;
        overflow-y: auto;
        padding: 1;
    }
    
    #log {
        height: 60%;
        overflow-y: auto;
        border: solid $accent;
    }
    
    .sidebar-header {
        padding-left: 1;
        padding-top: 1;
    }

    RecipeItem {
        height: auto;
        padding: 1;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("/", "focus_search", "Search"),
        ("alt+d", "scroll_details_down", "Body ↓"),
        ("alt+u", "scroll_details_up", "Body ↑"),
        ("ctrl+d", "scroll_log_down", "Log ↓"),
        ("ctrl+u", "scroll_log_up", "Log ↑"),
    ]

    def __init__(self):
        super().__init__()
        self.theme = "dracula"
        self.recipes = []
        # Assumption: running from root where justfile is.
        # In a real app we might search or accept args.
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
        command_list = self.query_one("#command_list", CommandList)
        if command_list.index is not None:
            command_list.action_cursor_down()
        else:
            command_list.index = 0

    def action_list_cursor_up(self):
        """Move cursor up in the command list."""
        command_list = self.query_one("#command_list", CommandList)
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
        # Scroll roughly half a page or a set amount.
        # RichLog doesn't have scroll_page_down exposed directly in same way as scrollable,
        # but it inherits from Scrollable.
        log.scroll_page_down()

    def action_scroll_log_up(self):
        """Scroll log view up."""
        log = self.query_one("#log", RichLog)
        log.scroll_page_up()

    def compose(self) -> ComposeResult:
        yield Header()

        self.recipes = self.load_recipes()

        with Horizontal():
            with Vertical(id="sidebar"):
                yield Label("[bold]Recipes[/bold]", classes="sidebar-header")
                yield SearchInput(placeholder="Search...", id="search_input")
                # Populate list
                recipe_items = [RecipeItem(r) for r in self.recipes]
                yield CommandList(*recipe_items, id="command_list")

            with Vertical(id="main_content"):
                yield Static("Select a recipe to see details.", id="details")
                yield RichLog(id="log", highlight=True, markup=True)

        yield Footer()

    @on(Input.Changed, "#search_input")
    def on_search_changed(self, event: Input.Changed):
        query = event.value.lower()
        command_list = self.query_one("#command_list", CommandList)

        # Clear existing items
        command_list.clear()

        # Filter and re-populate
        for recipe in self.recipes:
            if query in recipe.name.lower() or (
                recipe.doc and query in recipe.doc.lower()
            ):
                command_list.append(RecipeItem(recipe))

        # Select first item if matches found
        if len(command_list.children) > 0:
            command_list.index = 0

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
        # Run the currently selected recipe
        command_list = self.query_one("#command_list", CommandList)
        if command_list.highlighted_child:
            self.initiate_run(command_list.highlighted_child.recipe)

    def initiate_run(self, recipe: Recipe):
        if recipe.arguments:

            def handler(result):
                if result and not result.cancelled:
                    # Construct positional arguments in order
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

        log.clear()

        log.write(f"\n[bold blue]Running {recipe.name}...[/bold blue]")

        async for line in JustRunner.run_recipe(recipe.name, args):
            log.write(line)


def run():
    app = JustApp()
    app.run()


if __name__ == "__main__":
    run()

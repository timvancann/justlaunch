from dataclasses import dataclass
from typing import Dict
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Label, Input, Button
from textual.containers import Vertical, Horizontal
from textual import on
from jl.parser import Recipe
from jl.cache import ArgumentCache


@dataclass
class FormResult:
    """Result returned from ArgumentForm."""

    arguments: Dict[str, str]
    cancelled: bool = False


class ArgumentForm(ModalScreen[FormResult]):
    """Modal screen to input arguments for a recipe."""

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]

    def __init__(self, recipe: Recipe, cache: ArgumentCache, justfile_path: str):
        super().__init__()
        self.recipe = recipe
        self.cache = cache
        self.justfile_path = justfile_path
        self.inputs: Dict[str, Input] = {}

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label(
                f"[bold]Arguments for {self.recipe.name}[/bold]", classes="header"
            )

            cached_args = self.cache.get_last_arguments(
                self.justfile_path, self.recipe.name
            )

            for arg in self.recipe.arguments:
                yield Label(f"{arg.name}:", classes="arg-label")

                value = cached_args.get(arg.name)
                if value is None and arg.default:
                    value = arg.default
                if value is None:
                    value = ""

                inp = Input(value=value, placeholder=arg.name, id=f"arg_{arg.name}")
                self.inputs[arg.name] = inp
                yield inp

            with Horizontal(id="buttons"):
                yield Button("Cancel", variant="error", id="cancel")
                yield Button("Run", variant="primary", id="submit")

    def on_mount(self):
        if self.inputs:
            first_input = list(self.inputs.values())[0]
            first_input.focus()

    @on(Button.Pressed, "#cancel")
    def action_cancel(self):
        self.dismiss(FormResult(arguments={}, cancelled=True))

    @on(Button.Pressed, "#submit")
    def action_submit(self):
        self._submit()

    @on(Input.Submitted)
    def on_input_submitted(self, event: Input.Submitted):
        self._submit()

    def _submit(self):
        args = {name: inp.value for name, inp in self.inputs.items()}

        self.cache.save_arguments(self.justfile_path, self.recipe.name, args)

        self.dismiss(FormResult(arguments=args, cancelled=False))

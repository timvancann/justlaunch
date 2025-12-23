import asyncio
from typing import AsyncGenerator, List, Optional


class JustRunner:
    """Handles execution of just recipes."""

    @staticmethod
    async def run_recipe(
        recipe_name: str, args: Optional[List[str]] = None
    ) -> AsyncGenerator[str, None]:
        """
        Runs a just recipe with arguments and yields output lines.
        """
        cmd = ["just", recipe_name]
        if args:
            cmd.extend(args)

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )

        # Read output line by line
        if process.stdout:
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                yield line.decode("utf-8").rstrip()

        await process.wait()

        if process.returncode != 0:
            yield f"[bold red]Exited with code {process.returncode}[/bold red]"
        else:
            yield "[bold green]Success[/bold green]"

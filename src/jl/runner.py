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

        if process.stdout:
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                yield line.decode("utf-8").rstrip()

        await process.wait()

        if process.returncode != 0:
            yield f"\033[1;31mExited with code {process.returncode}\033[0m"
        else:
            yield "\033[1;32mSuccess\033[0m"

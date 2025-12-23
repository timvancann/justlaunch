import pytest
from unittest.mock import AsyncMock, patch
from jl.runner import JustRunner


@pytest.mark.asyncio
async def test_run_recipe_success():
    with patch("asyncio.create_subprocess_exec") as mock_exec:
        # Mock process
        mock_process = AsyncMock()
        mock_process.stdout.readline = AsyncMock(
            side_effect=[b"Building project...\n", b"Done.\n", b""]
        )
        mock_process.wait.return_value = None
        mock_process.returncode = 0

        mock_exec.return_value = mock_process

        lines = []
        async for line in JustRunner.run_recipe("build"):
            lines.append(line)

        assert lines == [
            "Building project...",
            "Done.",
            "[bold green]Success[/bold green]",
        ]
        mock_exec.assert_called_with(
            "just",
            "build",
            stdout=pytest.importorskip("asyncio").subprocess.PIPE,
            stderr=pytest.importorskip("asyncio").subprocess.STDOUT,
        )


@pytest.mark.asyncio
async def test_run_recipe_failure():
    with patch("asyncio.create_subprocess_exec") as mock_exec:
        mock_process = AsyncMock()
        mock_process.stdout.readline = AsyncMock(side_effect=[b"Error!\n", b""])
        mock_process.wait.return_value = None
        mock_process.returncode = 1

        mock_exec.return_value = mock_process

        lines = []
        async for line in JustRunner.run_recipe("fail"):
            lines.append(line)

        assert lines == ["Error!", "[bold red]Exited with code 1[/bold red]"]

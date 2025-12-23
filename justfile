# A sample justfile for testing JustLaunch

# Run the linter
lint:
    uv run ruff format .
    uv run ruff check --fix .

# Run the TUI
run mode="tui":
    uv run jl --mode {{mode}}

# Build the project
build:
    uv build

# Deploy to a specific environment
deploy env:
    echo "Deploying to {{env}}"

# Test command with multiple arguments and default values
complex_test arg1 arg2="default" flag="false":
    echo "arg1: {{arg1}}, arg2: {{arg2}}, flag: {{flag}}"

# Stream logs for testing
dummy-stream count="5" delay="0.5":
    #!/usr/bin/env python3
    import time
    import sys
    count = int("{{count}}")
    delay = float("{{delay}}")
    print(f"Starting dummy stream with {count} items...")
    for i in range(count):
        print(f"Log line {i+1} - processing item...")
        sys.stdout.flush()
        time.sleep(delay)
    print("Done!")

docker build:
    docker build -t jl .
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

docker-build tag="latest":
    docker build -t jl:{{tag}} .

test:

# Interactive version bump [interactive]
bump-version:
    #!/usr/bin/env bash
    set -e
    
    # Check status
    if [ -n "$(git status --porcelain)" ]; then
        echo "Git working directory not clean. Please commit or stash changes first."
        exit 1
    fi

    # Dry run to see what will happen
    echo "Dry run:"
    uv run cz bump --dry-run
    read -p "Continue? [y/N] " confirm
    if [[ $confirm != [yY] && $confirm != [yY][eE][sS] ]]; then
        exit 1
    fi

    # Bump metadata files only (pyproject.toml, CHANGELOG.md)
    uv run cz bump --files-only
    
    # Sync lockfile
    uv lock
    
    # Commit
    git add pyproject.toml uv.lock CHANGELOG.md
    
    # Get the new version for the tag message
    new_version=$(grep '^version =' pyproject.toml | cut -d '"' -f2)
    
    # Commit
    git commit -m "bump: version $new_version"
    
    # Tag
    git tag "v$new_version"
    
    # Push
    echo "Pushing changes..."
    git push origin main
    git push origin "v$new_version"
    
    echo "Done! You can now run: uv tool upgrade justlaunch"
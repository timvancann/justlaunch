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
    current_version=$(grep '^version =' pyproject.toml | cut -d '"' -f2)
    echo "Current version: $current_version"
    read -p "Enter new version: " new_version
    
    if [ -z "$new_version" ]; then
        echo "Version cannot be empty."
        exit 1
    fi
    
    # Update pyproject.toml using python for safety
    uv run python -c "import re; c=open('pyproject.toml').read(); open('pyproject.toml','w').write(re.sub(r'version = \".*\"', f'version = \"$new_version\"', c, count=1))"
    
    echo "Updated pyproject.toml to $new_version"
    
    # Update lockfile
    uv lock
    
    # Commit and tag
    git add pyproject.toml uv.lock
    git commit -m "Bump version to $new_version"
    git tag "$new_version"
    
    # Push
    echo "Pushing changes..."
    git push origin main
    git push origin "$new_version"
    
    echo "Done! You can now run: uv tool upgrade justlaunch"
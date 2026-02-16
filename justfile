export COMPOSE_FILE := "docker-compose.local.yml"

## Just does not yet manage signals for subprocesses reliably, which can lead to unexpected behavior.
## Exercise caution before expanding its usage in production environments.
## For more information, see https://github.com/casey/just/issues/2473 .


# Default command to list all available commands.
default:
    @just --list

# build: Build python image.
build *args:
    @echo "Building python image..."
    @docker compose build {{args}}

# up: Start up containers.
up:
    @echo "Starting up containers..."
    @docker compose up -d --remove-orphans

# down: Stop containers.
down:
    @echo "Stopping containers..."
    @docker compose down

# prune: Remove containers and their volumes.
prune *args:
    @echo "Killing containers and removing volumes..."
    @docker compose down -v {{args}}

# logs: View container logs
logs *args:
    @docker compose logs -f {{args}}

# manage: Executes `manage.py` command.
manage +args:
    @docker compose run --rm django python ./manage.py {{args}}

# format: Format code with ruff
format:
    @echo "Formatting code with ruff..."
    @docker compose run --rm django ruff format .

# lint: Check code with ruff
lint:
    @echo "Checking code with ruff..."
    @docker compose run --rm django ruff check .

# lint-fix: Check and auto-fix code with ruff
lint-fix:
    @echo "Checking and fixing code with ruff..."
    @docker compose run --rm django ruff check --fix .

# lint-fix-unsafe: Check and auto-fix code with ruff (including unsafe fixes)
lint-fix-unsafe:
    @echo "Checking and fixing code with ruff (unsafe fixes enabled)..."
    @docker compose run --rm django ruff check --fix --unsafe-fixes .

# quality: Run both format and lint-fix
quality:
    @echo "Running code quality checks..."
    @just format
    @just lint-fix

# quality-unsafe: Run both format and lint-fix with unsafe fixes
quality-unsafe:
    @echo "Running code quality checks with unsafe fixes..."
    @just format
    @just lint-fix-unsafe

# djlint: Format Django templates with djlint
djlint:
    @echo "Formatting templates with djlint..."
    @docker compose run --rm django djlint --reformat kancraonewms/templates/

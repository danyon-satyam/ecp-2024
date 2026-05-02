"""
Docker helper script.

Provides simple commands for managing the Docker development environment.

Usage:
  python scripts/docker_run.py build     # Build the Docker image
  python scripts/docker_run.py start     # Start all services
  python scripts/docker_run.py stop      # Stop all services
  python scripts/docker_run.py logs      # View API logs
  python scripts/docker_run.py shell     # Open shell inside container
  python scripts/docker_run.py seed      # Seed database inside container
  python scripts/docker_run.py status    # Show running containers
"""
import sys
import subprocess


def run(command: str) -> None:
    """
    Execute a shell command and print it first so the user knows
    exactly what is running.

    Args:
        command: Shell command string to execute
    """
    print(f"\n→ Running: {command}\n")
    subprocess.run(command, shell=True)


def main() -> None:
    """Parse the command argument and run the appropriate Docker command."""
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1].lower()

    commands = {
        "build": "docker-compose build",
        "start": "docker-compose up -d",
        "stop": "docker-compose down",
        "restart": "docker-compose down && docker-compose up -d",
        "logs": "docker-compose logs -f api",
        "status": "docker-compose ps",
        "shell": "docker-compose exec api bash",
        "seed": (
            "docker-compose exec api "
            "python scripts/seed_database.py"
        ),
        "migrate": (
            "docker-compose exec api "
            "alembic upgrade head"
        ),
        "clean": "docker-compose down -v --rmi local",
    }

    if cmd not in commands:
        print(f"Unknown command: {cmd}")
        print(f"Available: {', '.join(commands.keys())}")
        return

    run(commands[cmd])


if __name__ == "__main__":
    main()
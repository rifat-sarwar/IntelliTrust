#!/usr/bin/env python3
"""
Alembic Migration Helper Script for IntelliTrust

This script provides convenient commands for managing database migrations.
"""

import subprocess
import sys
import os

def run_command(command):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print(f"stderr: {e.stderr}")
        return False

def main():
    if len(sys.argv) < 2:
        print("""
Alembic Migration Helper for IntelliTrust

Usage:
    python migrate.py <command> [options]

Commands:
    init                    - Initialize Alembic (already done)
    create <message>        - Create a new migration
    upgrade [revision]      - Apply migrations (default: head)
    downgrade [revision]    - Rollback migrations (default: -1)
    current                 - Show current migration
    history                 - Show migration history
    show <revision>         - Show migration details
    stamp <revision>        - Mark database as at revision without running migrations
    
Examples:
    python migrate.py create "Add user profile fields"
    python migrate.py upgrade
    python migrate.py downgrade
    python migrate.py current
        """)
        return

    command = sys.argv[1]
    
    if command == "create" and len(sys.argv) >= 3:
        message = sys.argv[2]
        success = run_command(f"alembic revision --autogenerate -m '{message}'")
        if success:
            print(f"\nMigration created successfully!")
            print("Review the generated migration file and run 'python migrate.py upgrade' to apply it.")
    
    elif command == "upgrade":
        revision = sys.argv[2] if len(sys.argv) > 2 else "head"
        success = run_command(f"alembic upgrade {revision}")
        if success:
            print(f"\nMigration upgraded to {revision} successfully!")
    
    elif command == "downgrade":
        revision = sys.argv[2] if len(sys.argv) > 2 else "-1"
        success = run_command(f"alembic downgrade {revision}")
        if success:
            print(f"\nMigration downgraded to {revision} successfully!")
    
    elif command == "current":
        run_command("alembic current")
    
    elif command == "history":
        run_command("alembic history")
    
    elif command == "show" and len(sys.argv) >= 3:
        revision = sys.argv[2]
        run_command(f"alembic show {revision}")
    
    elif command == "stamp" and len(sys.argv) >= 3:
        revision = sys.argv[2]
        success = run_command(f"alembic stamp {revision}")
        if success:
            print(f"\nDatabase stamped at {revision} successfully!")
    
    else:
        print(f"Unknown command: {command}")
        print("Run 'python migrate.py' for help.")

if __name__ == "__main__":
    main()

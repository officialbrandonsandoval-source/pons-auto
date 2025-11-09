"""Deploy and initialize production environment."""

import subprocess
import sys


def run_command(cmd: str):
    """Run shell command."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)
    print(result.stdout)


def deploy_production():
    """Deploy production environment."""
    
    print("=" * 60)
    print("SHIFTLY AUTO - PRODUCTION DEPLOYMENT")
    print("=" * 60)
    
    # Step 1: Build Docker images
    print("\n1. Building Docker images...")
    run_command("docker-compose -f docker-compose.prod.yml build")
    
    # Step 2: Start services
    print("\n2. Starting services...")
    run_command("docker-compose -f docker-compose.prod.yml up -d")
    
    # Step 3: Wait for database
    print("\n3. Waiting for database...")
    run_command("sleep 10")
    
    # Step 4: Initialize database
    print("\n4. Initializing database...")
    run_command("docker-compose -f docker-compose.prod.yml exec app python -m shiftly.init_db")
    
    # Step 5: Create seed data (optional)
    print("\n5. Creating seed data...")
    run_command("docker-compose -f docker-compose.prod.yml exec app python -m shiftly.seed_data")
    
    print("\n" + "=" * 60)
    print("✓ DEPLOYMENT COMPLETE!")
    print("=" * 60)
    print("\nAccess points:")
    print("  API: http://localhost:8000")
    print("  Docs: http://localhost:8000/docs")
    print("  Metrics: http://localhost:8000/metrics")
    print("\nTo view logs:")
    print("  docker-compose -f docker-compose.prod.yml logs -f")
    print("\nTo stop:")
    print("  docker-compose -f docker-compose.prod.yml down")


if __name__ == "__main__":
    deploy_production()

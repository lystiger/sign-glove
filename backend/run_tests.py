#!/usr/bin/env python3
"""
Test runner script for Sign Glove API.
Supports running different types of tests with coverage reporting.
"""
import subprocess
import sys
import os
import argparse
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{'='*50}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(command)}")
    print('='*50)
    
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running {description}:")
        print(f"Return code: {e.returncode}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False

def run_tests(test_type="all", coverage=True, verbose=False):
    """Run tests based on type."""
    base_command = ["python", "-m", "pytest"]
    
    if verbose:
        base_command.append("-v")
    
    if coverage:
        base_command.extend([
            "--cov=.",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov",
            "--cov-fail-under=70"
        ])
    
    if test_type == "unit":
        base_command.extend(["-m", "unit"])
    elif test_type == "integration":
        base_command.extend(["-m", "integration"])
    elif test_type == "auth":
        base_command.extend(["-m", "auth"])
    elif test_type == "api":
        base_command.extend(["-m", "api"])
    elif test_type == "fast":
        base_command.extend(["-m", "not slow"])
    elif test_type == "all":
        pass  # Run all tests
    else:
        print(f"Unknown test type: {test_type}")
        return False
    
    return run_command(base_command, f"{test_type} tests")

def run_linting():
    """Run code linting."""
    commands = [
        (["python", "-m", "flake8", "."], "Flake8 linting"),
        (["python", "-m", "black", "--check", "."], "Black code formatting check"),
        (["python", "-m", "isort", "--check-only", "."], "Import sorting check"),
    ]
    
    success = True
    for command, description in commands:
        if not run_command(command, description):
            success = False
    
    return success

def run_security_checks():
    """Run security checks."""
    commands = [
        (["python", "-m", "bandit", "-r", ".", "-f", "txt"], "Bandit security scan"),
    ]
    
    # Try to run safety if available
    try:
        import safety
        commands.append((["python", "-m", "safety", "scan", "--policy-file", ".safety-policy.yml"], "Safety dependency scan"))
    except ImportError:
        print("⚠️  Safety package not available (pydantic version conflict)")
        print("   Consider using 'pip install pip-audit' as an alternative")
    
    success = True
    for command, description in commands:
        if not run_command(command, description):
            success = False
    
    return success

def install_test_dependencies():
    """Install additional test dependencies."""
    print("Installing development dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements-dev.txt"], check=True)
        print("✅ Development dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install development dependencies")
        print("You can install them manually with: pip install -r requirements-dev.txt")

def main():
    parser = argparse.ArgumentParser(description="Run Sign Glove API tests")
    parser.add_argument(
        "--type", 
        choices=["all", "unit", "integration", "auth", "api", "fast"],
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--no-coverage", 
        action="store_true",
        help="Disable coverage reporting"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--lint", 
        action="store_true",
        help="Run linting checks"
    )
    parser.add_argument(
        "--security", 
        action="store_true",
        help="Run security checks"
    )
    parser.add_argument(
        "--install-deps", 
        action="store_true",
        help="Install test dependencies"
    )
    parser.add_argument(
        "--all-checks", 
        action="store_true",
        help="Run all checks (tests, linting, security)"
    )
    
    args = parser.parse_args()
    
    # Change to backend directory
    os.chdir(Path(__file__).parent)
    
    if args.install_deps:
        install_test_dependencies()
    
    success = True
    
    if args.all_checks or args.lint:
        print("\n🔍 Running linting checks...")
        if not run_linting():
            success = False
    
    if args.all_checks or args.security:
        print("\n🔒 Running security checks...")
        if not run_security_checks():
            success = False
    
    if args.all_checks or not (args.lint or args.security):
        print("\n🧪 Running tests...")
        if not run_tests(args.type, not args.no_coverage, args.verbose):
            success = False
    
    if success:
        print("\n✅ All checks passed!")
        sys.exit(0)
    else:
        print("\n❌ Some checks failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
LEGACY ARCHIVED TEST

This script has been moved from `backend/test_basic_functionality.py`.
It is retained for reference and should not be collected by pytest.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(backend_dir))

async def test_imports():
    """Test if all required modules can be imported."""
    print("Testing imports...")
    
    try:
        from core.settings import settings
        print("✓ Settings imported successfully")
        
        from core.database import client, test_connection
        print("✓ Database module imported successfully")
        
        from core.auth import require_admin, require_user, require_viewer
        print("✓ Auth module imported successfully")
        
        from routes import auth_routes, gestures, training_routes
        print("✓ Route modules imported successfully")
        
        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False

async def test_database_connection():
    """Test database connection."""
    print("\nTesting database connection...")
    
    try:
        from core.database import test_connection
        await test_connection()
        print("✓ Database connection successful")
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

async def test_settings():
    """Test settings configuration."""
    print("\nTesting settings...")
    
    try:
        from core.settings import settings
        
        # Check required settings
        required_settings = [
            'MONGO_URI', 'DB_NAME', 'SECRET_KEY', 
            'JWT_SECRET_KEY', 'CORS_ORIGINS'
        ]
        
        for setting in required_settings:
            if hasattr(settings, setting):
                value = getattr(settings, setting)
                if value:
                    print(f"✓ {setting}: {str(value)[:50]}...")
                else:
                    print(f"✗ {setting}: Empty or None")
                    return False
            else:
                print(f"✗ {setting}: Not found")
                return False
        
        print("✓ All required settings are configured")
        return True
    except Exception as e:
        print(f"✗ Settings test failed: {e}")
        return False

async def test_directory_structure():
    """Test if required directories exist."""
    print("\nTesting directory structure...")
    
    try:
        from core.settings import settings
        
        required_dirs = [
            settings.DATA_DIR,
            settings.AI_DIR,
            settings.RESULTS_DIR,
            settings.UPLOAD_DIR,
            settings.TTS_CACHE_DIR
        ]
        
        for directory in required_dirs:
            if os.path.exists(directory):
                print(f"✓ Directory exists: {directory}")
            else:
                print(f"✗ Directory missing: {directory}")
                # Try to create it
                try:
                    os.makedirs(directory, exist_ok=True)
                    print(f"  → Created directory: {directory}")
                except Exception as e:
                    print(f"  → Failed to create: {e}")
                    return False
        
        print("✓ All required directories are available")
        return True
    except Exception as e:
        print(f"✗ Directory test failed: {e}")
        return False

async def main():
    """Run all tests."""
    print("Sign Glove Backend - Basic Functionality Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_settings,
        test_directory_structure,
        test_database_connection
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("Test Results Summary:")
    print("=" * 50)
    
    test_names = [
        "Import Test",
        "Settings Test", 
        "Directory Structure Test",
        "Database Connection Test"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "PASS" if result else "FAIL"
        print(f"{name}: {status}")
    
    all_passed = all(results)
    print(f"\nOverall Status: {'PASS' if all_passed else 'FAIL'}")
    
    if not all_passed:
        print("\nRecommendations:")
        print("1. Check your .env file configuration")
        print("2. Ensure MongoDB is running and accessible")
        print("3. Verify all required dependencies are installed")
        print("4. Check file permissions for directory creation")
    
    return all_passed

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)



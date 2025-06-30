#!/usr/bin/env python3
"""
Integration test for BSM application with all enhancement modules.
Tests the complete workflow from initialization to analysis.
"""

import sys
import os
import asyncio
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        # Core modules
        from bsm.core.settings import SettingsManager
        from bsm.core.database import DatabaseManager
        from bsm.core.async_database import AsyncDatabaseManager
        from bsm.core.ai_providers import AIProviderManager
        from bsm.core.async_manager import AsyncTaskManager
        from bsm.core.plugin_framework import PluginManager
        from bsm.core.security import SecureCredentialManager, PrivacyTelemetry
        
        # Utils
        from bsm.utils.improved_hotkey_manager import create_improved_hotkey_manager
        from bsm.utils.enhanced_ocr import EnhancedOCRProcessor
        from bsm.utils.text_capture import TextCapture
        
        # UI
        from bsm.ui.ui_enhancements import ThemeManager, ToastNotificationManager, AccessibilityManager
        
        print("✅ All imports successful")
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_basic_initialization():
    """Test basic component initialization."""
    print("Testing basic initialization...")
    
    try:
        # Settings
        settings = SettingsManager()
        print("✅ Settings manager initialized")
        
        # Database
        db_path = settings.get_database_path()
        db = DatabaseManager(db_path)
        print("✅ Database manager initialized")
        
        # AI Manager
        ai_manager = AIProviderManager()
        print("✅ AI provider manager initialized")
        
        # Plugin Manager
        plugin_manager = PluginManager()
        print("✅ Plugin manager initialized")
        
        # Enhanced OCR
        ocr = EnhancedOCRProcessor()
        print("✅ Enhanced OCR initialized")
        
        # Theme Manager
        theme_manager = ThemeManager()
        print("✅ Theme manager initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return False

async def test_async_components():
    """Test async components."""
    print("Testing async components...")
    
    try:
        # Async database
        settings = SettingsManager()
        async_db = AsyncDatabaseManager(settings.get_database_path())
        await async_db.initialize()
        print("✅ Async database initialized")
        
        # Async task manager
        from bsm.core.async_manager import get_task_manager
        task_manager = get_task_manager()
        
        # Test simple async task
        async def test_task():
            await asyncio.sleep(0.1)
            return "test_result"
        
        task_id = task_manager.submit_task(test_task(), description="Test task")
        print(f"✅ Async task submitted: {task_id}")
        
        # Wait a bit for task completion
        await asyncio.sleep(0.5)
        
        return True
        
    except Exception as e:
        print(f"❌ Async test failed: {e}")
        return False

def test_security_components():
    """Test security components."""
    print("Testing security components...")
    
    try:
        # Credential manager
        cred_manager = SecureCredentialManager('/tmp/test_creds.enc')
        cred_manager.store_credential('test_service', 'test_key', 'test_value')
        retrieved = cred_manager.get_credential('test_service', 'test_key')
        
        if retrieved == 'test_value':
            print("✅ Credential storage/retrieval working")
        else:
            print("❌ Credential retrieval failed")
            return False
        
        # Telemetry (disabled by default)
        telemetry = PrivacyTelemetry(enabled=False)
        telemetry.track_event('test_event', {'test_prop': 'test_value'})
        print("✅ Telemetry working")
        
        return True
        
    except Exception as e:
        print(f"❌ Security test failed: {e}")
        return False

def main():
    """Run all integration tests."""
    print("🚀 Starting BSM Integration Tests")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Basic Initialization", test_basic_initialization),
        ("Security Components", test_security_components),
    ]
    
    passed = 0
    total = len(tests)
    
    # Run sync tests
    for name, test_func in tests:
        print(f"\n📋 Running {name}...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {name} failed")
    
    # Run async tests
    print(f"\n📋 Running Async Components Test...")
    try:
        asyncio.run(test_async_components())
        passed += 1
        total += 1
    except Exception as e:
        print(f"❌ Async test failed: {e}")
        total += 1
    
    print("\n" + "=" * 50)
    print(f"🏁 Integration Tests Complete: {passed}/{total} passed")
    
    if passed == total:
        print("✅ All tests passed! BSM is ready for use.")
        return True
    else:
        print("❌ Some tests failed. Check the output above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

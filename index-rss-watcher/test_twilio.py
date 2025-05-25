#!/usr/bin/env python3
"""
Test script for Twilio SMS and voice call functionality
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.notifier import Notifier
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)

def test_twilio_functionality():
    """Test Twilio SMS and voice call functionality"""
    print("📱 Testing Twilio Notification System")
    print("=" * 50)
    
    # Test 1: Credential validation
    print("\n1. Testing Twilio credentials...")
    try:
        is_valid = Notifier.test_credentials()
        if is_valid:
            print("✅ Twilio credentials are valid")
        else:
            print("❌ Twilio credentials are invalid or not configured")
            print("💡 Set up your credentials in .env file to test actual sending")
    except Exception as e:
        print(f"❌ Credential test failed: {e}")
        print("💡 This is expected if credentials are not configured")
    
    # Test 2: Test mode SMS
    print("\n2. Testing SMS in test mode...")
    test_message = """🚨 Index Change Alert
Title: S&P 500 Index Constituent Changes Announced
Published: Mon, 25 Dec 2024 10:00:00 GMT
Summary: Addition and deletion of constituents effective after market close...
Link: https://example.com/news/1"""
    
    try:
        success = Notifier.send(test_message, test_mode=True)
        if success:
            print("✅ SMS test mode successful")
        else:
            print("❌ SMS test mode failed")
    except Exception as e:
        print(f"❌ SMS test failed: {e}")
    
    # Test 3: Performance test
    print("\n3. Testing notification performance...")
    import time
    start_time = time.time()
    
    for i in range(10):
        Notifier.send(f"Performance test message {i+1}", test_mode=True)
    
    end_time = time.time()
    avg_time = (end_time - start_time) / 10
    print(f"✅ Average notification processing time: {avg_time:.3f}s")
    
    # Instructions for real testing
    print("\n📋 To test with real SMS/calls:")
    print("1. Create a .env file in the project root")
    print("2. Add your Twilio credentials:")
    print("   TWILIO_SID=your_account_sid")
    print("   TWILIO_TOKEN=your_auth_token")
    print("   TWILIO_FROM=+1234567890")
    print("   TWILIO_TO=+1234567890")
    print("   USE_VOICE=0  # 0 for SMS, 1 for voice calls")
    print("3. Run this script again")
    
    print("\n🎯 Twilio test completed!")

if __name__ == "__main__":
    test_twilio_functionality()
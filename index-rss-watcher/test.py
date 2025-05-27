#!/usr/bin/env python3
"""
Consolidated test suite for Index RSS Watcher
Tests RSS feed processing, filtering logic, and notification system
"""
import asyncio
import sys
import os
import time
import shutil
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.watcher import FeedWatcher
from src.notifier import Notifier
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)

class TestSuite:
    """Comprehensive test suite for all components"""
    
    def __init__(self):
        self.passed_tests = 0
        self.failed_tests = 0
        
    async def run_all_tests(self):
        """Run all tests in sequence"""
        print("🧪 Index RSS Watcher Test Suite")
        print("=" * 60)
        
        # Setup test environment
        self.setup_test_environment()
        
        # Run tests
        await self.test_rss_watcher()
        await self.test_filtering_logic()
        await self.test_csv_storage()
        await self.test_notifier()
        
        # Cleanup
        self.cleanup_test_environment()
        
        # Summary
        print("\n" + "=" * 60)
        print(f"📊 Test Summary: {self.passed_tests} passed, {self.failed_tests} failed")
        return self.failed_tests == 0
    
    def setup_test_environment(self):
        """Create test data directory"""
        if not os.path.exists("data"):
            os.makedirs("data")
        # Backup any existing CSV
        if os.path.exists("data/seen_entries.csv"):
            shutil.move("data/seen_entries.csv", "data/seen_entries.csv.backup")
            
    def cleanup_test_environment(self):
        """Clean up test artifacts"""
        # Remove test CSV
        if os.path.exists("data/seen_entries.csv"):
            os.remove("data/seen_entries.csv")
        # Restore backup if exists
        if os.path.exists("data/seen_entries.csv.backup"):
            shutil.move("data/seen_entries.csv.backup", "data/seen_entries.csv")
    
    async def test_rss_watcher(self):
        """Test RSS watcher core functionality"""
        print("\n📰 Testing RSS Watcher")
        print("-" * 40)
        
        watcher = FeedWatcher()
        
        # Test 1: Feed access
        print("1. Testing feed access...")
        try:
            accessible = await watcher.test_feed_access()
            if accessible:
                self._pass("Feed is accessible")
            else:
                self._info("Feed not accessible - will use mock data")
        except Exception as e:
            self._info(f"Feed access failed (expected without network): {e}")
        
        # Test 2: Mock RSS processing
        print("\n2. Testing RSS data processing...")
        mock_rss_data = self._get_mock_rss_data()
        
        try:
            watcher._process_feed(mock_rss_data.encode('utf-8'))
            self._pass("RSS processing completed")
        except Exception as e:
            self._fail(f"RSS processing failed: {e}")
            
    async def test_filtering_logic(self):
        """Test RSS entry filtering for 'replace' keyword"""
        print("\n🔍 Testing Filtering Logic (Simple 'replace' filter)")
        print("-" * 40)
        
        watcher = FeedWatcher()
        
        # Test cases: (title, description, should_match)
        test_cases = [
            # Should match - contains "replace" in description
            ("S&P 500 Index Changes", "XYZ Corp will replace ABC Inc in the S&P 500", True),
            ("Dow Jones Update", "Company A replaces Company B effective Monday", True),
            ("Index Constituent Change", "This replacement will take effect after close", True),
            ("Russell Index Update", "ACME Corp to replace Widget Inc", True),
            ("FTSE 100 Change", "BigCo is replacing SmallCo in the index", True),
            
            # Should NOT match - no "replace" in description
            ("Pegasystems Set to Join S&P MidCap 400", "Company joins the index effective Friday", False),
            ("Monthly Rebalancing", "Regular rebalancing of constituents", False),
            ("Market Report", "Index gained 2% this quarter", False),
            ("Coinbase Added to S&P 500", "Addition announced today", False),
            ("Company Removed from Index", "XYZ removed from Russell 2000", False),
        ]
        
        print("Testing 'replace' pattern matching...")
        for title, description, should_match in test_cases:
            # Create minimal RSS with single entry
            rss_data = f"""<?xml version="1.0" encoding="UTF-8"?>
            <rss version="2.0">
                <channel>
                    <item>
                        <title>{title}</title>
                        <link>https://example.com/test</link>
                        <guid>test-{hash(title)}</guid>
                        <description>{description}</description>
                    </item>
                </channel>
            </rss>"""
            
            # Track notifications
            original_send = Notifier.send
            notifications_sent = []
            Notifier.send = lambda text, test_mode=False: notifications_sent.append(text) or True
            
            try:
                watcher._process_feed(rss_data.encode('utf-8'))
                matched = len(notifications_sent) > 0
                
                if matched == should_match:
                    self._pass(f"'{title}' - Correctly {'matched' if matched else 'ignored'}")
                else:
                    self._fail(f"'{title}' - Expected {'match' if should_match else 'ignore'}, got {'match' if matched else 'ignore'}")
            finally:
                Notifier.send = original_send
                
    async def test_csv_storage(self):
        """Test CSV storage functionality"""
        print("\n💾 Testing CSV Storage")
        print("-" * 40)
        
        # Start fresh for this test
        watcher = FeedWatcher()
        initial_count = len(watcher.seen_ids)
        
        # Test 1: CSV file exists
        print("1. Testing CSV file creation...")
        if os.path.exists("data/seen_entries.csv"):
            self._pass("CSV file exists")
        else:
            self._info("CSV file will be created on first entry")
            
        # Test 2: Save and reload
        print("\n2. Testing save and reload...")
        test_entries = [
            ("test-entry-1", "Test Entry 1", "https://example.com/test1"),
            ("test-entry-2", "Test Entry 2", "https://example.com/test2"),
        ]
        
        for entry_id, title, link in test_entries:
            watcher._save_entry(entry_id, title, link)
            
        # Create new watcher to test loading
        watcher2 = FeedWatcher()
        new_count = len(watcher2.seen_ids)
        
        if new_count >= initial_count + 2:
            self._pass(f"CSV persistence working correctly (added 2 entries, total: {new_count})")
        else:
            self._fail(f"Expected at least {initial_count + 2} entries, got {new_count}")
            
        # Test 3: CSV format
        print("\n3. Testing CSV format...")
        if os.path.exists("data/seen_entries.csv"):
            with open("data/seen_entries.csv", 'r') as f:
                content = f.read()
                if "timestamp,entry_id,title,link" in content:
                    self._pass("CSV has correct headers")
                else:
                    self._fail("CSV missing expected headers")
        else:
            self._fail("CSV file not created")
            
    async def test_notifier(self):
        """Test notification system"""
        print("\n📱 Testing Notification System")
        print("-" * 40)
        
        # Test 1: Credential validation
        print("1. Testing Twilio credentials...")
        try:
            is_valid = Notifier.test_credentials()
            if is_valid:
                self._pass("Twilio credentials are valid")
            else:
                self._info("Twilio credentials not configured (expected in test environment)")
        except Exception as e:
            self._info(f"Credential test skipped: {e}")
            
        # Test 2: Test mode
        print("\n2. Testing notification in test mode...")
        test_message = """🚨 Index Change Alert
Title: S&P 500 Index Constituent Changes
Published: Mon, 25 Dec 2024 10:00:00 GMT
Link: https://example.com/test"""
        
        try:
            success = Notifier.send(test_message, test_mode=True)
            if success:
                self._pass("Test mode notification successful")
            else:
                self._fail("Test mode notification failed")
        except Exception as e:
            self._fail(f"Notification test failed: {e}")
            
        # Test 3: Performance
        print("\n3. Testing notification performance...")
        start_time = time.time()
        
        for i in range(10):
            Notifier.send(f"Performance test {i+1}", test_mode=True)
            
        avg_time = (time.time() - start_time) / 10
        if avg_time < 0.1:  # Should be very fast in test mode
            self._pass(f"Average notification time: {avg_time:.3f}s")
        else:
            self._warn(f"Notifications slower than expected: {avg_time:.3f}s")
            
    def _get_mock_rss_data(self):
        """Generate mock RSS data for testing"""
        return """<?xml version="1.0" encoding="UTF-8"?>
        <rss version="2.0">
            <channel>
                <title>S&P DJI Index News</title>
                <description>Index constituent changes and announcements</description>
                <item>
                    <title>S&P 500 Index Constituent Changes Announced</title>
                    <link>https://example.com/news/1</link>
                    <guid>news-1</guid>
                    <pubDate>Mon, 25 Dec 2024 10:00:00 GMT</pubDate>
                    <description>Addition and deletion of constituents effective after market close</description>
                </item>
                <item>
                    <title>Quarterly earnings report published</title>
                    <link>https://example.com/news/2</link>
                    <guid>news-2</guid>
                    <pubDate>Mon, 25 Dec 2024 09:00:00 GMT</pubDate>
                    <description>Regular earnings update, no index changes</description>
                </item>
                <item>
                    <title>Russell 2000 Index - Company XYZ to be added effective January 1st</title>
                    <link>https://example.com/news/3</link>
                    <guid>news-3</guid>
                    <pubDate>Mon, 25 Dec 2024 08:00:00 GMT</pubDate>
                    <description>Index addition announced by Russell Investments</description>
                </item>
            </channel>
        </rss>"""
        
    def _pass(self, message):
        """Record passed test"""
        print(f"✅ {message}")
        self.passed_tests += 1
        
    def _fail(self, message):
        """Record failed test"""
        print(f"❌ {message}")
        self.failed_tests += 1
        
    def _info(self, message):
        """Print info message"""
        print(f"ℹ️  {message}")
        
    def _warn(self, message):
        """Print warning message"""
        print(f"⚠️  {message}")


async def main():
    """Run the test suite"""
    suite = TestSuite()
    success = await suite.run_all_tests()
    
    if not success:
        sys.exit(1)
        
    print("\n✅ All tests completed successfully!")
    
    # Print setup instructions
    print("\n📋 To run in production:")
    print("1. Create a .env file with:")
    print("   TWILIO_SID=your_account_sid")
    print("   TWILIO_TOKEN=your_auth_token")
    print("   TWILIO_FROM=+1234567890")
    print("   TWILIO_TO=+1234567890")
    print("   USE_VOICE=0  # 0 for SMS, 1 for voice")
    print("2. Run: python3 -m src.main")


if __name__ == "__main__":
    asyncio.run(main())
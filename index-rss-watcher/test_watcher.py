#!/usr/bin/env python3
"""
Test script for RSS watcher functionality
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.store import EntryStore
from src.watcher import FeedWatcher
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)

async def test_rss_watcher():
    """Test the RSS watcher functionality"""
    print("🧪 Testing RSS Watcher")
    print("=" * 50)
    
    # Test 1: Feed access
    print("\n1. Testing feed access...")
    store = EntryStore("test_rss.db")  # Use file database for testing
    watcher = FeedWatcher(store)
    
    try:
        accessible = await watcher.test_feed_access()
        if accessible:
            print("✅ Feed is accessible")
        else:
            print("❌ Feed is not accessible - using mock data for testing")
    except Exception as e:
        print(f"❌ Feed access test failed: {e}")
    
    # Test 2: Mock RSS data processing
    print("\n2. Testing RSS data processing...")
    mock_rss_data = """<?xml version="1.0" encoding="UTF-8"?>
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
    
    try:
        watcher._process_feed(mock_rss_data.encode('utf-8'))
        print("✅ RSS processing test completed")
    except Exception as e:
        print(f"❌ RSS processing failed: {e}")
    
    # Test 3: Performance test
    print("\n3. Testing performance...")
    import time
    start_time = time.time()
    
    for i in range(5):
        watcher._process_feed(mock_rss_data.encode('utf-8'))
    
    end_time = time.time()
    avg_time = (end_time - start_time) / 5
    print(f"✅ Average processing time: {avg_time:.3f}s per feed")
    
    print("\n🎯 RSS Watcher test completed!")

if __name__ == "__main__":
    asyncio.run(test_rss_watcher())
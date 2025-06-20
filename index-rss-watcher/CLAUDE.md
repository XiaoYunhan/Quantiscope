# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Service
```bash
# Start the RSS watcher service
python3 -m src.main

# Alternative method
cd src && python3 main.py
```

### Testing
```bash
# Test RSS feed processing and filtering logic
python3 test_watcher.py

# Test Twilio SMS/voice notifications
python3 test_twilio.py
```

### Setup
```bash
# Install dependencies
pip3 install -r requirements.txt

# Create environment configuration
cp .env.template .env
# Then edit .env with your Twilio credentials
```

### Deployment
```bash
# systemd (Linux)
sudo cp deploy/index-rss.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable index-rss
sudo systemctl start index-rss

# Check status
sudo systemctl status index-rss
```

## Architecture Overview

This is an asyncio-based RSS monitoring service that watches S&P Global index feeds for constituent changes and sends real-time notifications via Twilio.

### Core Components

**main.py**: Entry point with graceful shutdown handling. Uses asyncio.wait() to manage concurrent tasks (RSS watcher + shutdown signal). Implements comprehensive error handling and logging.

**watcher.py**: The heart of the system. FeedWatcher class polls RSS feeds every 30 seconds using conditional HTTP requests (ETag/Last-Modified). Contains sophisticated filtering logic with multiple regex patterns to identify index constituent changes. Handles connection pooling and retry logic with exponential backoff.

**notifier.py**: Twilio integration with lazy client initialization. Supports both SMS and voice calls. Includes credential validation and test modes. Handles Twilio-specific formatting (emoji cleanup for voice calls, SMS character limits).

**store.py**: Simple SQLite wrapper for tracking processed RSS entries. Uses context managers for connection handling. Prevents duplicate notifications by storing entry IDs.

**config.py**: Environment configuration with SSL warning suppression. Loads from .env file with sensible defaults.

### Key Design Patterns

- **Async/await throughout**: All I/O operations are async to prevent blocking
- **Graceful shutdown**: Signal handlers and task cancellation for clean exits
- **Lazy initialization**: Twilio client only created when needed
- **Context managers**: Used for database connections and HTTP sessions
- **Fallback URL patterns**: Multiple RSS URLs attempted if primary fails
- **Conditional requests**: Uses HTTP caching headers to minimize bandwidth

### RSS Filtering Logic

The service uses a simple filter:
1. Checks if the description field contains "replace" (case-insensitive)
2. Only sends notifications for items with replacements
3. Sends the complete item content including full description

### Configuration Notes

- No quotes needed in .env file values
- Phone numbers must include country codes (+1234567890)
- USE_VOICE=0 for SMS, USE_VOICE=1 for voice calls
- POLL_INTERVAL_SEC defaults to 30 seconds
- SSL warnings are suppressed in config.py to avoid urllib3 compatibility notices

### Error Handling Strategy

- Database initialization failures exit immediately with code 1
- RSS fetch failures use exponential backoff (max 5 consecutive errors)
- Twilio failures are logged but don't stop RSS processing
- All exceptions are caught and logged at appropriate levels
- Service can recover from network issues and API rate limits

### Testing Strategy

- test.py: Comprehensive test suite that includes:
  - RSS feed access and processing tests
  - Pattern matching and filtering logic validation
  - CSV storage functionality tests
  - Twilio notification system tests (with test mode)
- Tests can run without real RSS feeds or Twilio credentials
- Creates temporary test data that's cleaned up after test completion

### Data Storage

- Seen RSS entries are stored in `data/seen_entries.csv`
- CSV format: timestamp, entry_id, title, link
- Human-readable format makes debugging easy
- No database dependencies, simplifying deployment
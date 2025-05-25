# Index RSS Watcher

A robust Python service that monitors S&P Global index RSS feeds for constituent changes and sends real-time SMS/voice notifications.

## Features

- = **Smart RSS Monitoring**: Monitors S&P Global index news with intelligent filtering for constituent changes
- =ñ **Multi-Channel Notifications**: Send alerts via SMS or voice calls using Twilio
- =€ **High Performance**: Optimized feed parsing with conditional requests and connection pooling
- =¾ **Persistent State**: SQLite database to track processed entries and prevent duplicates
- =á **Robust Error Handling**: Comprehensive error handling with retry logic and backoff
- ¡ **Fast Response**: Average processing time under 3ms per feed

## Quick Start

### 1. Setup Environment

```bash
# Clone and navigate to project
cd index-rss-watcher

# Install dependencies
pip3 install -r requirements.txt

# Create environment configuration
cp .env.template .env
```

### 2. Configure Twilio (for notifications)

1. Sign up for a [Twilio account](https://www.twilio.com/try-twilio)
2. Get your Account SID and Auth Token from the [Twilio Console](https://console.twilio.com/)
3. Purchase a Twilio phone number
4. Update your `.env` file:

```env
TWILIO_SID=your_account_sid_here
TWILIO_TOKEN=your_auth_token_here
TWILIO_FROM=+1234567890  # Your Twilio number
TWILIO_TO=+1234567890    # Your mobile number
USE_VOICE=0              # 0 for SMS, 1 for voice calls
```

### 3. Run the Service

```bash
# Start the RSS watcher
python3 -m src.main

# Or run as a module
cd src && python3 main.py
```

## Testing

### Test RSS Feed Processing
```bash
python3 test_watcher.py
```

### Test Twilio Notifications
```bash
python3 test_twilio.py
```

## Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `FEED_URL` | RSS feed URL to monitor | S&P Global index news |
| `POLL_INTERVAL_SEC` | Polling interval in seconds | 30 |
| `DB_PATH` | SQLite database path | `./rss_state.db` |
| `TWILIO_SID` | Twilio Account SID | Required for notifications |
| `TWILIO_TOKEN` | Twilio Auth Token | Required for notifications |
| `TWILIO_FROM` | Twilio phone number | Required for notifications |
| `TWILIO_TO` | Destination phone number | Required for notifications |
| `USE_VOICE` | Notification type (0=SMS, 1=Voice) | 0 |

## Deployment

### Using systemd (Linux)

```bash
# Copy service file
sudo cp deploy/index-rss.service /etc/systemd/system/

# Edit paths in service file
sudo nano /etc/systemd/system/index-rss.service

# Enable and start service
sudo systemctl enable index-rss
sudo systemctl start index-rss

# Check status
sudo systemctl status index-rss
```

### Using Docker

```bash
# Build image
docker build -t index-rss-watcher .

# Run container
docker run -d --name rss-watcher \
  --env-file .env \
  index-rss-watcher
```

## How It Works

1. **RSS Monitoring**: Polls the S&P Global RSS feed every 30 seconds using conditional HTTP requests
2. **Content Filtering**: Uses multiple regex patterns to identify index constituent changes
3. **Duplicate Prevention**: SQLite database tracks processed entries by ID
4. **Notification Delivery**: Sends formatted alerts via Twilio SMS or voice calls
5. **Error Recovery**: Automatic retry with exponential backoff on failures

## Filtering Logic

The service identifies index changes using these patterns:
- Explicit terms: "constituent", "addition", "deletion", "changes"
- Index-specific: "S&P", "Dow", "Russell", "FTSE" + change terms
- Action terms: "effective", "announced", "added", "removed", "replacing"

## Troubleshooting

### RSS Feed Issues
- The S&P Global RSS may block requests - the service tries multiple URL patterns
- Check logs for HTTP 403 errors and consider using alternative RSS sources

### Twilio Issues
- Verify credentials in the Twilio Console
- Ensure phone numbers include country codes (e.g., +1234567890)
- Check account balance and verify your phone number

### Performance Issues
- Default 30-second polling interval can be adjusted via `POLL_INTERVAL_SEC`
- Service uses connection pooling and conditional requests for efficiency

## Logs

The service logs to stdout with structured formatting:
```
2024-12-25 10:00:00,123 INFO watcher: Fetch completed in 0.45s
2024-12-25 10:00:30,456 INFO watcher: Processing feed with 15 entries
2024-12-25 10:01:15,789 INFO notifier: SMS sent: SM1234567890abcdef
```

## Support

For issues and questions:
1. Check the logs for error messages
2. Run the test scripts to isolate problems
3. Verify configuration in `.env` file
4. Ensure all dependencies are installed
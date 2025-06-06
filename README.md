# Quantiscope

A collection of quantitative finance tracking and monitoring services designed for real-time financial data surveillance and alerting.

## Overview

Quantiscope provides specialized services for monitoring various financial data sources, processing updates in real-time, and delivering notifications through multiple channels. Each service is designed to be independent, scalable, and reliable.

## Services

### index-rss-watcher
Monitors S&P Global RSS feeds for index constituent changes and delivers real-time notifications via SMS and voice calls. This service tracks additions, deletions, and other significant changes to major indices.

[View Documentation](index-rss-watcher/README.md)

## Architecture

Each service in Quantiscope follows these principles:

- **Asynchronous Design**: Built on async/await patterns for efficient resource utilization
- **State Persistence**: Maintains operational state across restarts
- **Multi-Channel Notifications**: Supports various notification methods (SMS, voice, email, etc.)
- **Error Resilience**: Comprehensive error handling and automatic recovery
- **Configuration Flexibility**: Environment-based configuration for different deployment scenarios

## Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/Quantiscope.git
   cd Quantiscope
   ```

2. Navigate to the service you want to use:
   ```bash
   cd index-rss-watcher
   ```

3. Follow the service-specific setup instructions in its README.md

## Development

For development guidelines and patterns, see [CLAUDE.md](CLAUDE.md).

## Requirements

- Python 3.8 or higher
- Service-specific dependencies (see individual service directories)

## Contributing

1. Create a feature branch from `main`
2. Make your changes following the established patterns
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

[Specify your license here]

## Support

For issues and questions, please use the GitHub issue tracker.
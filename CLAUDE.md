# Quantiscope Development Guide

## Overview
Quantiscope is a collection of quantitative finance tracking and monitoring services. This repository contains various tools and services for monitoring financial data sources and providing timely notifications.

## Repository Structure
```
Quantiscope/
├── index-rss-watcher/    # S&P Global index RSS feed monitoring service
└── [future services]     # Additional quantitative tracking services
```

## Services

### index-rss-watcher
A high-performance RSS feed monitoring service for S&P Global index constituents. See [index-rss-watcher/CLAUDE.md](index-rss-watcher/CLAUDE.md) for detailed development guide.

## Common Development Patterns

### Architecture Principles
- **Microservice Design**: Each service is self-contained with its own dependencies
- **Asynchronous Processing**: Services use async/await patterns for efficient I/O operations
- **Configuration Management**: Environment-based configuration using .env files
- **State Persistence**: Services maintain state across restarts
- **Error Resilience**: Comprehensive error handling and recovery mechanisms

### Testing Strategy
- Unit tests for core functionality
- Integration tests for external service interactions
- Mock external dependencies during testing
- Continuous integration via GitHub Actions

### Deployment
- Systemd service files for production deployment
- Environment variable configuration
- Graceful shutdown handling
- Automatic restart on failure

## Adding New Services
When adding a new quantitative tracking service:
1. Create a new directory at the repository root
2. Include service-specific README.md and CLAUDE.md
3. Follow the established patterns from existing services
4. Add appropriate GitHub Actions workflows
5. Document configuration requirements

## Development Environment
- Python 3.8+ for Python-based services
- Virtual environment isolation
- Service-specific requirements.txt
- Local .env files (not committed)

## CI/CD
GitHub Actions workflows are configured at the repository level in `.github/workflows/`. Each service should have its own workflow triggered by changes to its directory.
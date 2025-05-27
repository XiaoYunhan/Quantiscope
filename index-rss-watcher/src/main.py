import asyncio, logging, sys, signal, os
import warnings
from .watcher import FeedWatcher

# Suppress urllib3 SSL warnings
warnings.filterwarnings("ignore", message="urllib3.*", category=UserWarning)

# Setup logging with rotation
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

log = logging.getLogger("main")

# Global shutdown flag - will be initialized in main()
shutdown_event = None

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    log.info(f"Received signal {signum}, initiating graceful shutdown...")
    shutdown_event.set()

async def main():
    """Main application entry point with error handling"""
    global shutdown_event
    shutdown_event = asyncio.Event()
    
    try:
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        log.info("Starting Index RSS Watcher...")
        
        # Initialize components
        try:
            watcher = FeedWatcher()
            log.info("RSS Watcher initialized")
        except Exception as e:
            log.error(f"Failed to initialize watcher: {e}")
            return 1
        
        # Run the watcher with shutdown handling
        try:
            watcher_task = asyncio.create_task(watcher.run_forever())
            shutdown_task = asyncio.create_task(shutdown_event.wait())
            
            # Wait for either the watcher to fail or shutdown signal
            done, pending = await asyncio.wait(
                [watcher_task, shutdown_task],
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # Cancel remaining tasks
            for task in pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
            # Check if watcher failed
            if watcher_task in done:
                try:
                    await watcher_task
                except Exception as e:
                    log.error(f"Watcher failed: {e}")
                    return 1
            
            log.info("Shutdown complete")
            return 0
            
        except Exception as e:
            log.error(f"Runtime error: {e}")
            return 1
    
    except Exception as e:
        log.error(f"Fatal error: {e}")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        log.info("Received keyboard interrupt")
        sys.exit(0)
    except Exception as e:
        log.error(f"Unhandled exception: {e}")
        sys.exit(1)

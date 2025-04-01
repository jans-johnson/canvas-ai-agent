import asyncio
import signal
import sys

from app.logger import logger
from app.agent.canvasai import CanvasAI
from app.utils.loading_utils import LoadingAnimation

# For clean shutdown
async def shutdown(signal, loop):
    """Cleanup tasks tied to the service's shutdown."""
    logger.info(f"Received exit signal {signal.name}...")
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    
    logger.info(f"Cancelling {len(tasks)} outstanding tasks")
    for task in tasks:
        task.cancel()
    
    await asyncio.gather(*tasks, return_exceptions=True)
    logger.info("Shutdown complete.")
    loop.stop()

async def main():
    try:
        # Setup signal handlers
        loop = asyncio.get_running_loop()
        signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
        for s in signals:
            loop.add_signal_handler(
                s, lambda s=s: asyncio.create_task(shutdown(s, loop))
            )
        
        # Initialize the agent
        logger.info("Initializing Canvas AI agent")
        agent = CanvasAI()
        
        # Authenticate user
        with LoadingAnimation("Authenticating with Canvas", "spinner"):
            auth_result = agent.authenticate_user()
        
        if not auth_result:
            print("Authentication failed. Please check your Canvas API key.")
            return
        
        # Load active courses
        with LoadingAnimation("Loading your courses", "spinner"):
            courses = agent.load_active_courses()
        
        if not courses:
            print("No active courses found or error loading courses.")
            return
        
        print("\nWelcome to the Canvas Academic Assistant!")
        print("Ask me about your courses, assignments, deadlines, or grades.")
        print("Type 'exit' to quit.")

        while True:
            prompt = input("\nYou: ")
            
            if prompt.lower() in ['exit', 'quit', 'bye']:
                print("Goodbye!")
                break
            if not prompt.strip():
                logger.warning("Empty prompt provided.")
                continue
                
            # Process the query
            logger.info(f"Processing query: {prompt}")
            
            # The loading animations are now handled within the agent.process_query method
            response = agent.process_query(prompt)
            print(f"\nAssistant: {response}")

    except KeyboardInterrupt:
        logger.warning("Operation interrupted.")
        # Clean exit - no need to re-raise
    except asyncio.CancelledError:
        # Task was cancelled, exit gracefully
        pass
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise


if __name__ == "__main__":
    try:
        # Clear the terminal at startup for better visibility
        if sys.platform.startswith('win'):
            # For Windows
            _ = system('cls')
        else:
            # For Unix-like systems
            _ = system('clear')
    except:
        # If system call fails, just continue
        pass
        
    print("Starting Canvas AI...")
    asyncio.run(main())

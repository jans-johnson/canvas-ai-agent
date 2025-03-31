import asyncio

from app.logger import logger
from app.agent.canvasai import canvasAI

async def main():
    try:
        agent = canvasAI()
        if not agent.authenticate_user():
            print("Authentication failed. Please check your Canvas API key.")
            return
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
                return
            # Process the query
            logger.warning("Processing your request...")
            response = agent.process_query(prompt)
            print(f"\nAssistant: {response}")

        await agent.run(prompt)
        logger.info("Request processing completed.")
    except KeyboardInterrupt:
        logger.warning("Operation interrupted.")


if __name__ == "__main__":
    asyncio.run(main())

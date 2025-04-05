# Updated main.py
from os import system
import os
import signal
import sys
import webbrowser
import threading
import time
from flask import Flask, render_template, request, jsonify
import atexit

from app.logger import logger
from app.agent.canvasai import CanvasAI
from app.config import SHOW_LOGS

# Global variable to track exit request
exit_requested = False
agent = None
app = Flask(__name__, 
            static_folder="static",
            template_folder="templates")

def cleanup():
    """Perform cleanup operations before exit"""
    logger.info("Performing cleanup operations...")
    # Add any specific cleanup needed for the agent
    if agent:
        # Close any open connections or resources
        pass
    logger.info("Cleanup complete")

def signal_handler(sig, frame):
    """Handle termination signals gracefully."""
    global exit_requested
    logger.info(f"Received exit signal {sig}...")
    exit_requested = True
    cleanup()
    logger.info("Shutdown complete.")
    sys.exit(0)

def open_browser():
    """Open the browser after a short delay to ensure Flask is running"""
    time.sleep(1)
    webbrowser.open('http://127.0.0.1:5000')

@app.route('/')
def home():
    """Render the main chat interface"""
    return render_template('index.html')

@app.route('/api/query', methods=['POST'])
def process_query():
    """API endpoint to process queries"""
    global agent
    
    if not agent:
        return jsonify({"error": "Agent not initialized"}), 500
        
    data = request.json
    query = data.get('query', '')
    
    if not query.strip():
        return jsonify({"error": "Empty query provided"}), 400
        
    try:
        logger.info(f"Processing query: {query}")
        response = agent.process_query(query)
        return jsonify({"response": response})
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/courses', methods=['GET'])
def get_courses():
    """API endpoint to get user's courses"""
    global agent
    
    if not agent:
        return jsonify({"error": "Agent not initialized"}), 500
        
    try:
        courses = agent.load_active_courses()
        return jsonify({"courses": courses})
    except Exception as e:
        logger.error(f"Error loading courses: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/shutdown', methods=['POST'])
def shutdown():
    """API endpoint to gracefully shut down the application"""
    global exit_requested
    
    logger.info("Shutdown requested via API")
    
    # Function to shut down the server
    def shutdown_server():
        global exit_requested
        exit_requested = True
        # Give time for the response to be sent
        time.sleep(1)
        # Perform cleanup
        cleanup()
        # Exit the application
        logger.info("Shutdown complete.")
        os._exit(0)
    
    # Start shutdown in a separate thread to allow response to be sent
    threading.Thread(target=shutdown_server).start()
    
    return jsonify({"status": "Shutting down..."}), 200

def initialize_agent():
    """Initialize the Canvas AI agent and authenticate"""
    global agent
    
    logger.info("Initializing Canvas AI agent")
    agent = CanvasAI()
    
    logger.info("Authenticating with Canvas")
    auth_result = agent.authenticate_user()
    
    if not auth_result:
        logger.error("Authentication failed")
        return False
        
    logger.info("Authentication successful")
    return True

def main():
    try:
        # Setup signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        if hasattr(signal, 'SIGHUP'):  # Not available on Windows
            signal.signal(signal.SIGHUP, signal_handler)
        
        # Register the cleanup function to be called on exit
        atexit.register(cleanup)
        
        # Initialize the agent
        if not initialize_agent():
            print("Authentication failed. Please check your Canvas API key.")
            return
            
        # Start Flask in a separate thread
        threading.Thread(target=lambda: app.run(debug=False, use_reloader=False)).start()
        
        # Open browser
        threading.Thread(target=open_browser).start()
        
        print("\nWelcome to the Canvas Academic Assistant!")
        print("The web interface has been opened in your browser.")
        print("You can also access it at: http://127.0.0.1:5000")
        print("Press Ctrl+C to exit or use the Quit button in the application.")
        
        # Keep the main thread alive
        while not exit_requested:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.warning("Operation interrupted.")
        cleanup()
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        cleanup()
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
    main()
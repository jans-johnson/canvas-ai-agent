# Canvas Academic Assistant

Canvas Academic Assistant is an advanced, AI-driven conversational platform meticulously designed to revolutionize the way students interact with their Canvas Learning Management System (LMS). By leveraging state-of-the-art natural language processing (NLP) capabilities and seamless API integrations, this application empowers students to efficiently access academic information, manage coursework, and stay on top of deadlines.

## Key Features
- **Dynamic Course Management**: Retrieve and display active courses with real-time updates.
- **Comprehensive Assignment Insights**: Access detailed information about assignments, including deadlines, descriptions, and submission statuses.
- **Grade Analytics**: Provide granular insights into grades, enabling students to track academic performance effectively.
- **Deadline Tracking**: Aggregate and prioritize upcoming deadlines across all courses.
- **AI-Powered Query Resolution**: Utilize OpenAI's cutting-edge GPT models to interpret and respond to complex academic queries.
- **Intuitive Web Interface**: A user-centric design ensures seamless interaction with the chatbot, enhancing the overall user experience.

## Setup Instructions

### Prerequisites
- **Python Environment**: Ensure Python 3.8 or higher is installed.
- **Package Manager**: `pip` must be available for dependency management.

### Deployment Steps

1. **Clone the Repository**
   Clone the project repository to your local machine:
   ```bash
   git clone <repository-url>
   cd CanvasAi/Application
   ```

2. **Install Dependencies**
   Install all required Python libraries and frameworks specified in `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**
   - Duplicate the `.example.env` file and rename it to `.env`:
     ```bash
     cp .example.env .env
     ```
   - Populate the `.env` file with the following critical variables:
     - `OPENAI_API_KEY`: Your OpenAI API key for accessing GPT models.
     - `OPENAI_MODEL`: Specify the OpenAI model to be utilized (e.g., `gpt-4`).
     - `OPENAI_BASE_URL`: The endpoint for OpenAI's API.
     - `CANVAS_API_KEY`: Your Canvas API key for authenticating API requests.
     - `CANVAS_API_URL`: The base URL for your institution's Canvas LMS API.

4. **Launch the Application**
   Execute the following command to initiate the Flask server:
   ```bash
   python main.py
   ```
   The application will automatically open in your default web browser at `http://127.0.0.1:5000`.

5. **Interact with the Chatbot**
   Use the web interface to engage with the AI assistant. Ask questions about your courses, assignments, grades, or deadlines, and receive intelligent, context-aware responses.

## Architectural Overview
Canvas Academic Assistant is built on a robust architecture that integrates multiple technologies:
- **Backend Framework**: Flask serves as the backbone for API handling and server-side logic.
- **AI Integration**: OpenAI's GPT models power the natural language understanding and response generation.
- **Canvas API**: Seamlessly integrates with the Canvas LMS to fetch real-time academic data.
- **Frontend Interface**: A responsive and interactive web interface ensures a smooth user experience.

## Future Roadmap
- **Cross-LMS Compatibility**: Extend support to other LMS platforms such as Moodle and Blackboard.
- **Multi-Step Task Resolution**: Enable the agent to solve complex tasks by breaking them into multiple steps, allowing it to answer intricate queries comprehensively. The agent will intelligently search multiple areas within the Canvas API and synthesize a cohesive response for the student.
- **Additional Agents**: Introduce specialized agents, such as a web browsing agent for retrieving external academic resources and a file-saving agent for managing and storing important documents. These enhancements will significantly expand the application's functionality and versatility.
- **Predictive Analytics**: Provide students with actionable insights based on historical academic data.
- **Mobile Application**: Develop native apps for iOS and Android to enable on-the-go access.
- **Multi-Language Support**: Expand accessibility by supporting multiple languages for global users.

## License
This project is distributed under the MIT License. Refer to the LICENSE file for detailed terms and conditions.


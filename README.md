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
   git clone https://github.com/jans-johnson/canvas-ai-agent
   cd canvas-ai-agent
   ```

2. **Set Up a Virtual Environment**
   It is recommended to use a virtual environment to isolate the project's dependencies. Follow these steps using Conda:

   - Create a Conda virtual environment with Python 3.11:
     ```bash
     conda create --name canvas-ai-env python=3.11
     ```
   - Activate the virtual environment:
     ```bash
     conda activate canvas-ai-env
     ```
   - Once activated, your terminal prompt will change to indicate the Conda environment is active.

3. **Install Dependencies**
   Install all required Python libraries and frameworks specified in `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**
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

### Obtaining Canvas Access Tokens
To use the Canvas API, you need to generate an access token. Follow these steps:

1. **Log in to Canvas**: Access your institution's Canvas LMS and log in with your credentials.
2. **Navigate to Account Settings**: Click on your profile picture or name in the global navigation menu, then select "Settings."
3. **Generate a New Access Token**:
   - Scroll down to the "Approved Integrations" section.
   - Click the **+ New Access Token** button.
   - Provide a purpose for the token (e.g., "Canvas Academic Assistant") and set an expiration date if required.
   - Click **Generate Token**.
4. **Copy the Token**: Once the token is generated, copy it immediately. You will not be able to view it again later.
5. **Store the Token Securely**: Paste the token into the `.env` file under the `CANVAS_API_KEY` variable.

**Note**: Keep your access token confidential and do not share it with others. If the token is compromised, revoke it immediately from the "Approved Integrations" section in Canvas.

5. **Launch the Application**
   Execute the following command to initiate the Flask server:
   ```bash
   python main.py
   ```
   The application will automatically open in your default web browser at `http://127.0.0.1:5000`.

6. **Interact with the Chatbot**
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


// static/js/script.js
document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');
    const courseList = document.getElementById('course-list');
    const quitButton = document.getElementById('quit-button');
    const clearChatButton = document.getElementById('clear-chat');

    // Load courses when the page loads
    loadCourses();

    // Handle form submission
    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const message = chatInput.value.trim();
        if (!message) return;
        
        // Add user message to chat
        addMessage(message, 'user');
        
        // Clear input
        chatInput.value = '';
        
        // Show typing indicator
        showTypingIndicator();
        
        // Send message to backend
        sendMessage(message);
    });

    // Handle clear chat button click
    clearChatButton.addEventListener('click', function() {
        if (confirm('Are you sure you want to clear the chat history?')) {
            // Keep only the welcome message
            const welcomeMessage = chatMessages.firstElementChild;
            chatMessages.innerHTML = '';
            chatMessages.appendChild(welcomeMessage);
            
            // Add a system message
            addMessage('Chat history has been cleared.', 'assistant');
        }
    });

    // Handle quit button click
    quitButton.addEventListener('click', function() {
        if (confirm('Are you sure you want to quit the application?')) {
            // Add a message to the chat
            addMessage('Shutting down the application...', 'assistant');
            
            // Call the shutdown endpoint
            fetch('/api/shutdown', {
                method: 'POST'
            })
            .then(response => {
                if (response.ok) {
                    // Show a final message before the window closes
                    addMessage('Shutdown successful. You can close this window.', 'assistant');
                    
                    // Disable the quit button to prevent multiple shutdown requests
                    quitButton.disabled = true;
                    quitButton.innerHTML = '<i class="fas fa-check"></i> Application Shutting Down';
                    quitButton.style.backgroundColor = '#888';
                } else {
                    addMessage('Failed to shut down the application. Please close the window manually.', 'assistant');
                }
            })
            .catch(error => {
                console.error('Error shutting down:', error);
                addMessage('Error shutting down the application. Please close the window manually.', 'assistant');
            });
        }
    });

    // Function to load courses
    function loadCourses() {
        fetch('/api/courses')
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    courseList.innerHTML = `<div class="course-item"><i class="fas fa-exclamation-circle"></i> Error: ${data.error}</div>`;
                    return;
                }
                
                if (!data.courses || data.courses.length === 0) {
                    courseList.innerHTML = '<div class="course-item"><i class="fas fa-info-circle"></i> No courses found</div>';
                    return;
                }
                
                courseList.innerHTML = '';
                data.courses.forEach(course => {
                    const courseItem = document.createElement('div');
                    courseItem.className = 'course-item';
                    courseItem.innerHTML = `<i class="fas fa-book"></i> ${course.name}`;
                    courseItem.dataset.courseId = course.id;
                    
                    // Add click event to populate the chat input
                    courseItem.addEventListener('click', () => {
                        const query = `Tell me about my ${course.name} course`;
                        chatInput.value = query;
                        chatInput.focus();
                        
                        // Add visual feedback
                        courseItem.style.backgroundColor = 'var(--sidebar-hover)';
                        setTimeout(() => {
                            courseItem.style.backgroundColor = '';
                        }, 300);
                    });
                    
                    courseList.appendChild(courseItem);
                });
            })
            .catch(error => {
                console.error('Error loading courses:', error);
                courseList.innerHTML = '<div class="course-item"><i class="fas fa-exclamation-triangle"></i> Failed to load courses</div>';
            });
    }

    // Function to send message to backend
    function sendMessage(message) {
        fetch('/api/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query: message })
        })
        .then(response => response.json())
        .then(data => {
            // Remove typing indicator
            removeTypingIndicator();
            
            if (data.error) {
                addMessage(`Error: ${data.error}`, 'assistant');
                return;
            }
            
            addMessage(data.response, 'assistant');
        })
        .catch(error => {
            console.error('Error sending message:', error);
            removeTypingIndicator();
            addMessage('Sorry, there was an error processing your request.', 'assistant');
        });
    }

    // Function to add message to chat with timestamp
    function addMessage(message, sender) {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${sender}-message`;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        // Replace newlines with <br> tags
        const formattedMessage = message.replace(/\n/g, '<br>');
        messageContent.innerHTML = `<p>${formattedMessage}</p>`;
        
        // Add timestamp
        const timestamp = document.createElement('div');
        timestamp.className = 'message-timestamp';
        timestamp.textContent = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        
        messageElement.appendChild(messageContent);
        messageElement.appendChild(timestamp);
        chatMessages.appendChild(messageElement);
        
        // Add animation class
        messageElement.classList.add('animate-in');
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Function to show typing indicator
    function showTypingIndicator() {
        const typingIndicator = document.createElement('div');
        typingIndicator.className = 'typing-indicator';
        typingIndicator.id = 'typing-indicator';
        
        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('span');
            typingIndicator.appendChild(dot);
        }
        
        chatMessages.appendChild(typingIndicator);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Function to remove typing indicator
    function removeTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    // Auto-resize input field as user types
    chatInput.addEventListener('input', function() {
        this.style.height = 'auto';
        const maxHeight = 120; // Maximum height in pixels
        this.style.height = Math.min(this.scrollHeight, maxHeight) + 'px';
    });

    // Focus input on page load
    chatInput.focus();
});
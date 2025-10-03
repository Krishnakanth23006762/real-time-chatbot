Real-Time Web Assistant Chatbot
🚀 Overview
This project is a sophisticated, AI-driven chatbot built with Python and Streamlit. It provides real-time, accurate answers to user queries by leveraging the power of the Google Gemini API with integrated web search. The application features a secure user authentication system, including registration, 2FA (Two-Factor Authentication) via email OTP, and a password reset workflow.

✨ Key Features
Real-Time Web Search: Instead of relying on static documents, the chatbot uses the Gemini API with Google Search grounding to fetch and synthesize up-to-date information from the internet, providing current and relevant answers.

Secure User Authentication: A complete user management system that includes:

User Registration: New users can create an account with their email and a password.

Sign-In with 2FA: Existing users sign in with their credentials, followed by a secure One-Time Password (OTP) sent to their registered email.

Forgot/Reset Password: A secure workflow allows users to reset their password via a time-sensitive link sent to their email.

Persistent User Data: User accounts are stored in a persistent SQLite database, ensuring that user information is retained between sessions and application restarts.

Content Moderation: Includes a built-in profanity filter to check user input and maintain a professional interaction environment.

Modern & Responsive UI: Built with Streamlit, the user interface is clean, modern, and works seamlessly on both desktop and mobile browsers.

🛠️ Technology Stack
Backend & Frontend: Streamlit

Language Model: Google Gemini API (gemini-2.5-flash)

Database: SQLite (for user management)

Core Libraries: requests, better-profanity, smtplib

⚙️ Setup and Usage
To run this project locally, please follow these steps:

Clone the Repository

git clone [https://github.com/your-username/real-time-chatbot.git](https://github.com/your-username/real-time-chatbot.git)
cd real-time-chatbot

Create and Activate a Virtual Environment

# Create the environment
python -m venv venv
# Activate on Windows
.\venv\Scripts\activate

Install Dependencies

pip install -r requirements.txt

Configure Your Secrets

Create a folder named .streamlit in the project root.

Inside .streamlit, create a file named secrets.toml.

Add your credentials to the file in the following format:

[email_credentials]
sender_email = "your_email@gmail.com"
sender_password = "your_16_character_google_app_password"

[google_ai]
api_key = "your_gemini_api_key"

Run the Application

streamlit run app.py

📄 License
This project is for demonstration and educational purposes. All rights are reserved. The code is provided for viewing and learning, and it is not licensed for reuse, modification, or distribution without express written permission from the author.

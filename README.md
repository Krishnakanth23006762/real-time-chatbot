## Saveetha Engineering College - HR Policy AI Assistant

# Project Overview

# This project is an intelligent chatbot designed to serve as an AI Assistant for the faculty and staff of Saveetha Engineering College (SEC). It provides quick and accurate answers to questions regarding the college's HR policies and procedures by leveraging internal documents.

The primary goal is to enhance organizational efficiency by making policy information easily accessible through a conversational interface.

Key Features

Internal Knowledge Base: Answers questions based only on the official SEC HR policy documents provided.

RAG Pipeline: Utilizes a Retrieval-Augmented Generation (RAG) system to find relevant information within the documents and generate concise answers.

Secure Authentication: Features a robust login system:

User registration with email and password.

Secure sign-in with password verification.

Two-Factor Authentication (2FA) via email OTP.

"Forgot Password" functionality with secure reset links.

Document Analysis Tools: Allows authenticated users to upload their own PDF documents for:

Summarization: Get quick bullet-point summaries.

Keyword Extraction: Identify key topics within the document.

Content Filtering: Includes a profanity filter to maintain a professional interaction environment.

Custom UI: Features a user interface themed with Saveetha Engineering College branding.

Persistent User Data: Uses an SQLite database (user_database.db) to store user accounts securely.

Technology Stack

Backend & UI: Python, Streamlit

AI/NLP: LangChain, Hugging Face Transformers (all-MiniLM-L6-v2 for embeddings, google/flan-t5-base for generation), FAISS (for vector storage)

Database: SQLite

Authentication: Custom implementation using Python's hashlib and smtplib.

Content Filtering: better-profanity

Setup and Usage (Local Development)

Clone the repository:

git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
cd your-repo-name


Create and activate a virtual environment:

python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate # MacOS/Linux


Install dependencies:

pip install -r requirements.txt


Configure Secrets:

Create a folder named .streamlit in the project root.

Inside .streamlit, create a file named secrets.toml.

Add your Gmail credentials (email and a 16-character App Password) under the [email_credentials] section. See app.py comments for details.

Prepare Knowledge Base:

Create a folder named data.

Place all internal SEC policy documents (PDFs, DOCX) inside the data folder.

Run the setup script: python rag_setup.py. This creates the faiss_index_combined folder.

Run the application:

streamlit run app.py


Target Audience

This application is intended for use by the faculty and staff of Saveetha Engineering College.

License

This project is licensed under the GNU Affero General Public License v3.0 (AGPLv3).

The AGPLv3 is a strong copyleft license specifically designed for network server software. It ensures that if you modify the code and run it on a server to offer services to others, you must provide the source code of your modified version to those users.

You can find the full license text in the LICENSE file included in this repository.

Note on Usage: While the license permits modification and distribution under its terms, this specific application is tailored for Saveetha Engineering College and relies on its internal documents. It is provided primarily for demonstration and educational purposes.

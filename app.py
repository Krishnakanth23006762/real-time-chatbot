# app.py (Final Stable Version - SEC Theme with Standard Layout)

import streamlit as st
import smtplib
import random
from email.message import EmailMessage
from better_profanity import profanity
import database as db
import os
import tempfile

# --- RAG Imports for Internal Search ---
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_huggingface import HuggingFacePipeline
from langchain_core.prompts import PromptTemplate
from langchain_community.document_loaders import PyPDFLoader

# --- 0. Initialize Database ---
db.setup_database()

# --- Page Config ---
st.set_page_config(
    page_title="Saveetha HR Assistant",
    page_icon="https://www.saveetha.ac.in/images/sec-logo.png",
    layout="wide"
)

# --- CUSTOM UI STYLES ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');
    
    html, body, [class*="st-"], .stButton>button {
        font-family: 'Poppins', sans-serif;
    }
    .stButton>button {
        border-radius: 12px;
        border: 1px solid #FFC425; /* SEC Gold */
        background-color: #FFC425; /* SEC Gold */
        color: #002366; /* Dark text on gold button */
        font-weight: 600;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        border: 1px solid #E0A800;
        background-color: #E0A800;
    }
</style>
""", unsafe_allow_html=True)

# --- Authentication and Email Functions ---
def send_email(receiver_email, subject, body):
    try:
        sender_email = st.secrets["email_credentials"]["sender_email"]
        sender_password = st.secrets["email_credentials"]["sender_password"]
    except (KeyError, FileNotFoundError):
        st.error("Email credentials not found. Please configure your secrets.toml file.")
        return False
    
    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Failed to send email. Error: {e}")
        return False

def show_auth_pages():
    query_params = st.query_params
    
    if "page" in query_params and query_params["page"] == "reset_password" and "token" in query_params:
        st.session_state.page_state = "reset_password"
        st.session_state.reset_token = query_params["token"]
    
    if 'page_state' not in st.session_state:
        st.session_state.page_state = "main"

    if st.session_state.page_state == "main":
        st.title("Welcome to the Saveetha HR Policy Assistant")
        col1, col2 = st.columns(2)
        if col1.button("Sign In", use_container_width=True):
            st.session_state.page_state = "signin"
            st.rerun()
        if col2.button("Register", use_container_width=True):
            st.session_state.page_state = "register"
            st.rerun()

    elif st.session_state.page_state == "register":
        st.title("Register New Account")
        with st.form("register_form"):
            email = st.text_input("Email Address")
            password = st.text_input("Set Password", type="password")
            if st.form_submit_button("Register"):
                if db.add_user(email, password):
                    st.success("Registration successful! Please proceed to Sign In.")
                    st.session_state.page_state = "signin"
                    st.rerun()
                else:
                    st.error("This email is already registered.")
        if st.button("← Back"):
            st.session_state.page_state = "main"
            st.rerun()

    elif st.session_state.page_state == "signin":
        st.title("Sign In")
        with st.form("signin_form"):
            email = st.text_input("Email Address")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Sign In"):
                if db.verify_user(email, password):
                    otp = str(random.randint(100000, 999999))
                    st.session_state.otp_code = otp
                    st.session_state.user_email = email
                    if send_email(email, "Your Login Code", f"Your One-Time Password (OTP) is: {otp}"):
                        st.session_state.page_state = "otp"
                        st.rerun()
                else:
                    st.error("Invalid email or password.")
        if st.button("Forgot Password?", type="secondary"):
            st.session_state.page_state = "forgot_password"
            st.rerun()
        if st.button("← Back"):
            st.session_state.page_state = "main"
            st.rerun()

    elif st.session_state.page_state == "otp":
        st.title("Verify Your Identity")
        st.info(f"A verification code has been sent to {st.session_state.user_email}.")
        with st.form("otp_form"):
            otp_input = st.text_input("Enter the 6-digit code", max_chars=6)
            if st.form_submit_button("Verify"):
                if otp_input == st.session_state.get("otp_code"):
                    st.session_state.authenticated = True
                    for key in ["page_state", "otp_code", "reset_token"]:
                        if key in st.session_state: del st.session_state[key]
                    st.rerun()
                else:
                    st.error("The code is incorrect.")

    elif st.session_state.page_state == "forgot_password":
        st.title("Forgot Password")
        with st.form("forgot_password_form"):
            email = st.text_input("Enter your registered email address")
            if st.form_submit_button("Send Reset Link"):
                token = db.set_reset_token(email)
                if token:
                    app_base_url = "http://localhost:8501" 
                    reset_link = f"{app_base_url}?page=reset_password&token={token}"
                    body = f"Click the link to reset your password: {reset_link}\nThis link is valid for one hour."
                    if send_email(email, "Password Reset", body):
                        st.success("A password reset link has been sent to your email.")
                else:
                    st.error("If this email is registered, a reset link has been sent.")
        if st.button("← Back to Sign In"):
            st.session_state.page_state = "signin"
            st.rerun()

    elif st.session_state.page_state == "reset_password":
        st.title("Reset Your Password")
        token = st.session_state.get("reset_token")
        with st.form("reset_password_form"):
            new_password = st.text_input("Enter new password", type="password")
            confirm_password = st.text_input("Confirm new password", type="password")
            if st.form_submit_button("Reset Password"):
                if new_password and new_password == confirm_password:
                    if db.reset_password(token, new_password):
                        st.success("Your password has been reset successfully! Please sign in.")
                        st.session_state.page_state = "signin"
                        del st.session_state.reset_token
                        st.query_params.clear()
                        st.rerun()
                    else:
                        st.error("Invalid or expired reset link.")
                else:
                    st.error("Passwords do not match.")

# --- Main App Logic (Runs only if authenticated) ---
if not st.session_state.get("authenticated", False):
    show_auth_pages()
else:
    # --- Caching and Resource Loading for RAG ---
    @st.cache_resource
    def load_rag_resources():
        print("Loading RAG resources...")
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vectorstore = FAISS.load_local("faiss_index_combined", embeddings, allow_dangerous_deserialization=True)
        llm = HuggingFacePipeline.from_model_id(
            model_id="google/flan-t5-base",
            task="text2text-generation",
            model_kwargs={"temperature": 0.1, "max_length": 512},
            device=-1 # Use CPU
        )
        prompt_template = """
        Use the context from the documents to answer the question concisely and clearly.
        If you don't know the answer from the context provided, say that you don't have information on that topic.
        
        Context: {context}
        Question: {question}
        
        Answer: """
        PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vectorstore.as_retriever(search_type="mmr", search_kwargs={"k": 3}),
            return_source_documents=True,
            chain_type_kwargs={"prompt": PROMPT}
        )
        print("RAG resources loaded successfully.")
        return qa_chain, llm

    qa_chain, llm = load_rag_resources()

    st.title("📘 Saveetha HR Policy Assistant")

    # --- Sidebar ---
    with st.sidebar:
        st.image("https://www.saveetha.ac.in/images/sec-logo.png", width=150)
        st.header("📄 Document Tools")
        st.info("Upload a document for a quick analysis.")
        
        uploaded_file = st.file_uploader("Upload a PDF document", type=['pdf'])

        col1, col2 = st.columns(2)
        summarize_button = col1.button("Summarize", use_container_width=True)
        keywords_button = col2.button("Keywords", use_container_width=True)

        if uploaded_file and (summarize_button or keywords_button):
            with st.spinner("Analyzing document..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    loader = PyPDFLoader(tmp_file.name)
                    text = " ".join(page.page_content for page in loader.load())[:15000]

                    if "analysis_result" in st.session_state:
                        del st.session_state.analysis_result

                    if summarize_button:
                        prompt_text = f"Summarize this document in 5 clear bullet points:\n\n{text}"
                        st.session_state.analysis_result = llm.invoke(prompt_text)
                    elif keywords_button:
                        prompt_text = f"Extract the 10 most important keywords or topics from this text as a comma-separated list:\n\n{text}"
                        st.session_state.analysis_result = llm.invoke(prompt_text)
                os.remove(tmp_file.name)

        if "analysis_result" in st.session_state:
            st.success("Analysis complete:")
            st.write(st.session_state.analysis_result)
            if st.button("Clear Analysis"):
                del st.session_state.analysis_result
                st.rerun()

        st.write("---")
        if st.button("Logout"):
            for key in st.session_state.keys():
                del st.session_state[key]
            st.rerun()

    # --- Main Chat Interface ---
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Hello! How can I assist you with the HR policies today?"}]

    bot_logo_url = "https://www.saveetha.ac.in/images/sec-logo.png"
    user_logo_url = "https://cdn.icon-icons.com/icons2/1378/PNG/512/avatardefault_92824.png" 

    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar=bot_logo_url if message["role"] == "assistant" else user_logo_url):
            st.markdown(message["content"])

    greetings = ["hi", "hello", "hey"]
    
    if prompt := st.chat_input("Ask about college policies..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar=user_logo_url):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar=bot_logo_url):
            full_response = ""
            if profanity.contains_profanity(prompt):
                full_response = "I cannot process requests with inappropriate language."
            elif prompt.lower().strip() in greetings:
                full_response = "Hello! How can I assist you with our college policies today?"
            else:
                with st.spinner("Searching internal documents..."):
                    result = qa_chain.invoke({"query": prompt})
                    answer = result["result"]
                    sources = result.get("source_documents")
                    if sources:
                        doc_names = list(set([os.path.basename(s.metadata.get('source', 'N/A')) for s in sources]))
                        full_response = f"{answer}\n\n*Sources: {', '.join(doc_names)}*"
                    else:
                        full_response = answer
            
            st.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})


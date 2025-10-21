# rag_setup.py (For creating the internal knowledge base)

import os
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

DATA_PATH = "data/"
FAISS_INDEX_PATH = "faiss_index_combined"

# --- 1. Load all documents from the data folder ---
all_documents = []
print("Loading internal documents from the data folder...")

# Check if the data directory exists
if not os.path.exists(DATA_PATH):
    print(f"Error: The directory '{DATA_PATH}' was not found. Please create it and add your documents.")
else:
    for filename in os.listdir(DATA_PATH):
        file_path = os.path.join(DATA_PATH, filename)
        
        if filename.endswith(".pdf"):
            try:
                loader = PyPDFLoader(file_path)
                print(f"Loading PDF: {filename}")
                all_documents.extend(loader.load())
            except Exception as e:
                print(f"Error loading {filename}: {e}")
        elif filename.endswith(".docx"):
            try:
                loader = Docx2txtLoader(file_path)
                print(f"Loading DOCX: {filename}")
                all_documents.extend(loader.load())
            except Exception as e:
                print(f"Error loading {filename}: {e}")

    if not all_documents:
        print("No documents were loaded. Please check the 'data' folder and your file types.")
    else:
        print(f"\nLoaded a total of {len(all_documents)} pages/sections.")

        # --- 2. Split the documents into chunks ---
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        docs = text_splitter.split_documents(all_documents)
        print(f"Split documents into {len(docs)} chunks.")

        # --- 3. Create embeddings and store in FAISS index ---
        print("Creating embeddings and building the vector store... (This may take a moment)")
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vectorstore = FAISS.from_documents(docs, embeddings)

        # Save the combined vectorstore locally
        vectorstore.save_local(FAISS_INDEX_PATH)

        print(f"✅ Internal knowledge base created successfully at '{FAISS_INDEX_PATH}'!")


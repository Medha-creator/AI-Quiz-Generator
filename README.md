# AI Quiz Generator

An AI-powered quiz generation application that uses a PDF document as the knowledge source and generates multiple-choice questions based on a user-provided topic.

## Features

- Upload a PDF document
- Enter a topic or question
- Extract text from the uploaded PDF
- Split the extracted text into smaller chunks
- Generate embeddings using Hugging Face
- Store document embeddings in ChromaDB
- Retrieve relevant content using similarity search
- Use Retrieval-Augmented Generation (RAG)
- Generate 5 multiple-choice questions using Qwen
- Display the generated quiz in a React frontend

## Tech Stack

### Backend

- Python
- FastAPI
- PyPDF
- LangChain
- Hugging Face Embeddings
- ChromaDB
- Hugging Face Inference Providers
- Qwen/Qwen2.5-72B-Instruct

### Frontend

- React
- Vite
- JavaScript
- CSS

## How It Works

1. The user uploads a PDF and enters a topic or question.
2. FastAPI receives the PDF and the question.
3. Text is extracted from the PDF using PyPDF.
4. The extracted text is cleaned and divided into chunks.
5. Hugging Face embeddings convert the chunks into vectors.
6. ChromaDB stores the document vectors.
7. Relevant chunks are retrieved based on the user's question.
8. The retrieved content is provided as context to the Qwen language model.
9. Qwen generates exactly 5 MCQs in JSON format.
10. The React frontend displays the generated quiz.

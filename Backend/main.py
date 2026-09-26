from fastapi import FastAPI, UploadFile, File, Form
from pypdf import PdfReader
from dotenv import load_dotenv
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from huggingface_hub import InferenceClient
import json
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()

app.add_middleware(
  CORSMiddleware,
  allow_origins=["http://localhost:5173"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

hf_token = os.getenv("HF_TOKEN")

client = InferenceClient(
    api_key=hf_token,
    provider="auto"
)

if hf_token:
    print("Hugging Face token loaded successfully!")
else:
    print("Hugging Face token NOT found!")


embeddings = HuggingFaceEmbeddings(
  model_name="sentence-transformers/all-MiniLM-L6-v2"
)

@app.get("/")
def home():
  return {
    "message": "AI Quiz Generator Backend is running!",
    "hf_configured": bool(os.getenv("HF_TOKEN"))}

@app.post("/upload-pdf")
async def upload_pdf(
  question: str = Form(...),
  file: UploadFile = File(...)
):
  file_path = os.path.join("uploads", file.filename)

  with open(file_path, "wb") as buffer:
    buffer.write(await file.read())

  reader = PdfReader(file_path)

  text = ""

  for page in reader.pages:
    text += page.extract_text() or ""

  text = " ".join(text.split())

  if not text:
    return {
      "message": "No text could be extracted from the PDF"
    }

  text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=100
  )

  chunks = text_splitter.split_text(text)

  vectorstore = Chroma.from_texts(
    texts=chunks,
    embedding=embeddings,
    collection_name="pdf_documents",
    persist_directory="chroma_db"
  )

  retriever = vectorstore.as_retriever(
    search_kwargs={"k" : 3}
  )

  results = retriever.invoke(question)

  context = "\n\n".join([doc.page_content for doc in results])

  response = client.chat.completions.create(
    model="Qwen/Qwen2.5-72B-Instruct",
    messages=[
      {
        "role": "user",
        "content": f"""
  You are an AI quiz generator.

  Based only on the following context, generate 5 multiple-choice questions.

  Context:
  {context}

  for each question provide:
  1. The question
  2. Four options: A, B, C, D
  3. The correct answer

  Do not use information that is not present in the context.

  Topic:
  {question}

  Return the result as a JSON array in exactly this format:
  
    [
        {{
            "question": "Question text",
            "options": {{
                "A": "Option A",
                "B": "Option B",
                "C": "Option C",
                "D": "Option D"
            }},
            "correct_answer": "A"
        }}
    ]


Rules:
- Generate exactly 5 questions.
- Each question must have exactly 4 options: A, B, C, and D.
- The correct_answer must be one of: A, B, C, or D.
- Use only information from the provided context.
- Do not include any information that is not present in the context.
- Return only valid JSON.
- Do not use Markdown or code fences.
  """
      }
    ],
    max_tokens=1000
  )

  quiz = json.loads(response.choices[0].message.content)

  if len(quiz) != 5:
    raise ValueError("Quiz must contain exactly 5 questions")

  for item in quiz:
    if not all(key in item for key in ["question", "options", "correct_answer"]):
      raise ValueError("Each question must contain question, options, and correct_answer")

    if set(item["options"].keys()) != {"A", "B", "C", "D"}:
      raise ValueError("Each question must have exactly four options: A, B, C and D")

    if item["correct_answer"] not in {"A", "B", "C", "D"}:
      raise ValueError("Correct answer must be A, B, C, or D")

  return {
    "message": "Quiz generated successfully",
    "filename": file.filename,
    "quiz": quiz,
  }
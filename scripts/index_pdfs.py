import os
import glob
from pypdf import PdfReader
from pinecone import Pinecone, ServerlessSpec
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Initialize Pinecone
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
INDEX_NAME = "vaaniai-products"

# Initialize Gemini Client
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def chunk_text(text, chunk_size=1000, overlap=100):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def process_pdfs(pdf_dir="data/pdfs"):
    # Create index if not exists
    if INDEX_NAME not in [idx.name for idx in pc.list_indexes()]:
        pc.create_index(
            name=INDEX_NAME,
            dimension=768, # text-embedding-004 dimension
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
    index = pc.Index(INDEX_NAME)

    pdf_files = glob.glob(os.path.join(pdf_dir, "*.pdf"))
    if not pdf_files:
        print("No PDFs found in", pdf_dir)
        return
        
    for pdf_path in pdf_files:
        print(f"Processing {pdf_path}...")
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            if page.extract_text():
                text += page.extract_text() + "\n"
            
        chunks = chunk_text(text)
        print(f"Created {len(chunks)} chunks.")
        
        for i, chunk in enumerate(chunks):
            # Generate embedding using Google GenAI
            response = client.models.embed_content(
                model='text-embedding-004',
                contents=chunk,
            )
            embedding = response.embeddings[0].values
            
            # Upsert to Pinecone
            metadata = {
                "source": os.path.basename(pdf_path),
                "text": chunk
            }
            index.upsert(vectors=[(f"{os.path.basename(pdf_path)}-chunk-{i}", embedding, metadata)])
            print(f"Upserted chunk {i+1}/{len(chunks)}")

if __name__ == "__main__":
    process_pdfs()

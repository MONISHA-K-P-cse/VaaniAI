import os
import time
from pinecone import Pinecone, ServerlessSpec
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Configuration
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
INDEX_NAME = "vaaniai-products"

if not PINECONE_API_KEY or not GEMINI_API_KEY:
    print("Error: PINECONE_API_KEY and GEMINI_API_KEY must be set in .env")
    exit(1)

pc = Pinecone(api_key=PINECONE_API_KEY)
client = genai.Client(api_key=GEMINI_API_KEY)

# Sample Knowledge Base Data
KNOWLEDGE_BASE = [
    {
        "id": "prod_1",
        "text": "VaaniAI Tractor Loan Service: We offer loans for all major tractor brands like Mahindra, John Deere, and Tafe. Interest rates start at 8.5% per annum. Documentation required includes Aadhar Card, PAN Card, and 7/12 land records. Repayment tenure is flexible up to 7 years."
    },
    {
        "id": "prod_2",
        "text": "VaaniAI Crop Insurance: Protect your crops against unseasonal rain, drought, and pests. Premium is only 2% of the sum insured for Kharif crops and 1.5% for Rabi crops. Claims are settled within 30 days of assessment."
    },
    {
        "id": "prod_3",
        "text": "VaaniAI Digital Mandi: Get real-time market prices (Bhav) for your produce. We connect you directly with certified buyers. Commission is just 1%, much lower than local agents (Arhatiyas)."
    },
    {
        "id": "company_info",
        "text": "VaaniAI is an AI-first Relationship Manager for rural India. We support English, Hindi, and Tamil. Our goal is to bring financial inclusion through voice-first technology."
    }
]

def seed():
    print(f"Checking for Pinecone index: {INDEX_NAME}...")
    
    # Create index if it doesn't exist
    if INDEX_NAME in pc.list_indexes().names():
        desc = pc.describe_index(INDEX_NAME)
        if desc.dimension != 3072:
            print(f"Dimension mismatch (found {desc.dimension}, need 3072). Deleting index...")
            pc.delete_index(INDEX_NAME)
            time.sleep(5)
            
    if INDEX_NAME not in pc.list_indexes().names():
        print(f"Creating index {INDEX_NAME} with 3072 dimensions...")
        pc.create_index(
            name=INDEX_NAME,
            dimension=3072, 
            metric='cosine',
            spec=ServerlessSpec(cloud='aws', region='us-east-1')
        )
        # Wait for index to be ready
        while not pc.describe_index(INDEX_NAME).status['ready']:
            time.sleep(2)
    
    index = pc.Index(INDEX_NAME)
    
    print("Generating embeddings and uploading data...")
    for item in KNOWLEDGE_BASE:
        print(f"Processing: {item['id']}")
        embed_resp = client.models.embed_content(
            model='gemini-embedding-2',
            contents=item['text'],
        )
        vector = embed_resp.embeddings[0].values
        
        index.upsert(vectors=[(item['id'], vector, {"text": item['text']})])
    
    print("Seeding complete! Your knowledge base is ready for the demo.")

if __name__ == "__main__":
    seed()

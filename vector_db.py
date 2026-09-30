from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb


# Create ChromaDB client
client = chromadb.PersistentClient(
    path="chroma_db"
)


# Create collection
policy_db = client.get_or_create_collection(
    name="business_policy"
)


# Load PDF and store chunks
def create_policy_database(
    filename="Comprehensive_Corporate_Operations_Manual.pdf"
):

    reader = PdfReader(filename)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"


    # Split text into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )

    policy_chunks = text_splitter.split_text(text)


    # Add chunks to ChromaDB
    ids = [
        f"policy_{i}"
        for i in range(len(policy_chunks))
    ]

    policy_db.add(
        documents=policy_chunks,
        ids=ids
    )

    print("Policy added to ChromaDB")


# Retrieve relevant policy
def retrieve_policy(question):

    results = policy_db.query(
        query_texts=[question],
        n_results=3
    )

    documents = results["documents"][0]

    context = "\n\n".join(documents)

    return context



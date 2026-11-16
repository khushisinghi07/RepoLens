import uuid
import chromadb
from pathlib import Path
from app.config import settings
from app.services.chunker import collect_chunks
from app.services.embeddings import embed_texts

client = chromadb.PersistentClient(path=settings.chroma_path)

def index_repository(root: Path, display_name: str):
    chunks = collect_chunks(root)
    if not chunks:
        raise ValueError("No supported source files were found in this ZIP.")
    repo_id = str(uuid.uuid4())
    collection = client.create_collection("repo_" + repo_id.replace("-", ""), metadata={"hnsw:space": "cosine"})
    for offset in range(0, len(chunks), 64):
        batch = chunks[offset:offset+64]
        collection.add(
            ids=[f"chunk_{offset+i}" for i in range(len(batch))],
            documents=[x["text"] for x in batch],
            embeddings=embed_texts([x["text"] for x in batch]),
            metadatas=[{"file_path":x["file_path"],"start_line":x["start_line"],"end_line":x["end_line"]} for x in batch]
        )
    return {"repository_id":repo_id,"name":display_name,"files_indexed":len({x["file_path"] for x in chunks}),"chunks_indexed":len(chunks)}

def get_collection(repo_id):
    try:
        return client.get_collection("repo_" + repo_id.replace("-", ""))
    except Exception:
        return None

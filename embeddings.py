from functools import lru_cache
from sentence_transformers import SentenceTransformer
from app.config import settings

@lru_cache(maxsize=1)
def model():
    return SentenceTransformer(settings.embedding_model)

def embed_texts(texts):
    return model().encode(texts, normalize_embeddings=True, show_progress_bar=False).tolist()

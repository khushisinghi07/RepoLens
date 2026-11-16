# RepoLens — Codebase Intelligence & RAG Assistant

Upload a repository ZIP, index source code with local embeddings + ChromaDB, then ask questions and receive Gemini answers grounded in retrieved code chunks with file/line references.

## Stack
React + Vite · FastAPI · Sentence Transformers · ChromaDB · Google Gemini

## Run locally
### Backend (Python 3.10+)
```bash
cd backend
python -m venv .venv
# Windows: .venv\\Scripts\\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env
# Edit .env and set GEMINI_API_KEY (Google AI Studio: https://aistudio.google.com/apikey)
uvicorn app.main:app --reload
```
### Frontend (Node 18+)
```bash
cd frontend
npm install
npm run dev
```
Open http://localhost:5173. API docs: http://localhost:8000/docs.

Upload a ZIP file (up to 50 MB), wait for indexing, then ask questions about the repository. The first indexing run downloads the embedding model. Gemini API key is required for answers.

## API
- `GET /api/health`
- `POST /api/repositories/upload` (multipart field: `file`, ZIP only)
- `POST /api/chat` (JSON: `repository_id`, `question`)
- `GET /api/repositories/{repository_id}`

## Structure
```text
backend/app/       FastAPI app, chunker, embeddings, indexer, RAG
frontend/src/      React interface
```

## Notes
ChromaDB and embeddings run locally. Retrieved code context is sent to Gemini to generate answers. Avoid uploading secrets, `.env` files, private keys, or code you do not have permission to share. Large repositories may take time to index. This version indexes uploaded ZIPs; GitHub URL import, authentication, streaming, tests and deployment are future enhancements.

## License
MIT

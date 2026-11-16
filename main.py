from pathlib import Path
from zipfile import ZipFile, BadZipFile
import shutil, uuid
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.schemas import ChatRequest
from app.services.indexer import index_repository, get_collection
from app.services.rag import answer_question

app = FastAPI(title="RepoLens API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173","http://127.0.0.1:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/api/health")
def health():
    return {"status":"ok","service":"RepoLens API"}

@app.post("/api/repositories/upload")
async def upload_repository(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".zip"):
        raise HTTPException(400, "Please upload a .zip repository.")
    token = str(uuid.uuid4())
    zip_path = Path(settings.upload_dir) / f"{token}.zip"
    extract_path = Path(settings.upload_dir) / token
    try:
        size = 0
        with zip_path.open("wb") as out:
            while chunk := await file.read(1024*1024):
                size += len(chunk)
                if size > settings.max_upload_mb*1024*1024:
                    raise HTTPException(413, f"ZIP exceeds {settings.max_upload_mb} MB.")
                out.write(chunk)
        with ZipFile(zip_path) as archive:
            for item in archive.infolist():
                member = Path(item.filename)
                if member.is_absolute() or ".." in member.parts:
                    raise HTTPException(400, "Unsafe path found inside ZIP.")
                if item.file_size > 10*1024*1024:
                    continue
            archive.extractall(extract_path)
        children = list(extract_path.iterdir())
        root = children[0] if len(children)==1 and children[0].is_dir() else extract_path
        return index_repository(root, file.filename[:-4])
    except BadZipFile:
        raise HTTPException(400, "The uploaded file is not a valid ZIP archive.")
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(500, f"Indexing failed: {exc}")
    finally:
        zip_path.unlink(missing_ok=True)
        shutil.rmtree(extract_path, ignore_errors=True)

@app.post("/api/chat")
def chat(payload: ChatRequest):
    try:
        return answer_question(payload.repository_id, payload.question)
    except LookupError as exc:
        raise HTTPException(404, str(exc))
    except RuntimeError as exc:
        raise HTTPException(503, str(exc))
    except Exception as exc:
        raise HTTPException(502, f"AI request failed: {exc}")

@app.get("/api/repositories/{repository_id}")
def repository_info(repository_id: str):
    collection = get_collection(repository_id)
    if collection is None:
        raise HTTPException(404, "Repository not found.")
    return {"repository_id":repository_id,"chunks_indexed":collection.count()}

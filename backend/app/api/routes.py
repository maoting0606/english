from fastapi import APIRouter
from pydantic import BaseModel
from app.schemas.common import ok
from app.services.parser import parse_word_text
from app.services.oss import oss_service
from app.services.search import rank_word_results

router = APIRouter(prefix="/api/v1")

class ParseTextRequest(BaseModel):
    text: str

class UploadUrlRequest(BaseModel):
    filename: str
    prefix: str = "documents"

class WordSearchRequest(BaseModel):
    query: str

@router.get("/health")
def health():
    return ok({"status": "ok"})

@router.post("/parse/text")
def parse_text(payload: ParseTextRequest):
    items = parse_word_text(payload.text)
    return ok({"items": [item.__dict__ for item in items]})

@router.post("/file/upload-url")
def upload_url(payload: UploadUrlRequest):
    key = oss_service.object_key(payload.prefix, payload.filename)
    return ok(oss_service.signed_placeholder(key, "upload"))

@router.get("/file/{file_id}/download-url")
def download_url(file_id: int):
    return ok(oss_service.signed_placeholder(f"documents/{file_id}/source.docx", "download"))

@router.post("/doc/create")
def create_doc(payload: ParseTextRequest):
    items = parse_word_text(payload.text)
    return ok({"document_id": 1, "status": "READY", "word_count": len(items), "items": [item.__dict__ for item in items]})

@router.get("/doc/list")
def doc_list():
    return ok({"items": [], "total": 0})

@router.get("/doc/{doc_id}")
def doc_detail(doc_id: int):
    return ok({"id": doc_id, "status": "READY"})

@router.get("/doc/{doc_id}/preview")
def doc_preview(doc_id: int):
    return ok({"id": doc_id, "blocks": []})

@router.delete("/doc/{doc_id}")
def delete_doc(doc_id: int):
    return ok({"id": doc_id, "status": "DELETED"})

@router.post("/word/search")
def word_search(payload: WordSearchRequest):
    demo = [{"word": payload.query, "source": "exact", "similarity": 1.0}]
    return ok({"items": rank_word_results(payload.query, demo)})

@router.get("/word/{word}")
def word_detail(word: str):
    return ok({"word": word, "forms": [], "occurrences": []})

@router.post("/ocr/task")
def create_ocr_task():
    return ok({"task_id": 10001, "status": "PENDING"})

@router.get("/ocr/task/{task_id}")
def ocr_task(task_id: int):
    return ok({"task_id": task_id, "status": "PENDING"})

@router.post("/audio/task")
def create_audio_task():
    return ok({"task_id": 10002, "status": "PENDING"})

@router.get("/audio/task/{task_id}")
def audio_task(task_id: int):
    return ok({"task_id": task_id, "status": "PENDING"})

@router.get("/error-record/list")
def error_list():
    return ok({"items": [], "total": 0})

@router.get("/task/{task_id}")
def task_detail(task_id: int):
    return ok({"task_id": task_id, "status": "PENDING"})

@router.get("/task/list")
def task_list():
    return ok({"items": [], "total": 0})

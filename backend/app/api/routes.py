from pathlib import Path
from tempfile import NamedTemporaryFile
from fastapi import APIRouter, Depends, File, Form, UploadFile
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.entities import Document, Task
from app.repositories.documents import create_document_from_items, create_ocr_result, list_documents, search_words
from app.schemas.common import ok
from app.services.docx_parser import parse_docx
from app.services.ocr import recognize_handwriting_placeholder
from app.services.oss import oss_service
from app.services.parser import parse_word_text
from app.services.search import rank_word_results

router = APIRouter(prefix="/api/v1")

class ParseTextRequest(BaseModel):
    text: str
    title: str = "粘贴文本"

class UploadUrlRequest(BaseModel):
    filename: str
    prefix: str = "documents"

class WordSearchRequest(BaseModel):
    query: str
    limit: int = 20

class OcrCheckRequest(BaseModel):
    document_id: int
    recognized_text: str

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

@router.post("/file/upload")
async def upload_file(file: UploadFile = File(...), prefix: str = Form("documents")):
    content = await file.read()
    key = oss_service.object_key(prefix, file.filename or "upload.bin")
    return ok({"object_key": key, "original_filename": file.filename, "content_type": file.content_type, "file_size": len(content), "upload_status": "UPLOADED"})

@router.get("/file/{file_id}/download-url")
def download_url(file_id: int):
    return ok(oss_service.signed_placeholder(f"documents/{file_id}/source.docx", "download"))

@router.post("/doc/create")
def create_doc(payload: ParseTextRequest, db: Session = Depends(get_db)):
    items = parse_word_text(payload.text)
    document = create_document_from_items(db, payload.title, "TEXT", items)
    return ok({"document_id": document.id, "status": document.status, "word_count": document.word_count, "items": [item.__dict__ for item in items]})

@router.post("/doc/upload")
async def upload_doc(title: str = Form("Word 文档"), file: UploadFile = File(...), db: Session = Depends(get_db)):
    suffix = Path(file.filename or "source.docx").suffix or ".docx"
    with NamedTemporaryFile(suffix=suffix, delete=True) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp.flush()
        items, _ = parse_docx(tmp.name)
    source_file = {"original_filename": file.filename, "object_key": oss_service.object_key("documents", file.filename or "source.docx"), "content_type": file.content_type, "file_size": len(content), "etag": None}
    document = create_document_from_items(db, title, "WORD", items, source_file)
    return ok({"document_id": document.id, "status": document.status, "word_count": document.word_count})

@router.get("/doc/list")
def doc_list(db: Session = Depends(get_db)):
    docs = list_documents(db)
    return ok({"items": [{"id": d.id, "title": d.title, "word_count": d.word_count, "status": d.status, "created_at": d.created_at} for d in docs], "total": len(docs)})

@router.get("/doc/{doc_id}")
def doc_detail(doc_id: int, db: Session = Depends(get_db)):
    document = db.get(Document, doc_id)
    return ok(None if document is None else {"id": document.id, "title": document.title, "status": document.status, "word_count": document.word_count})

@router.get("/doc/{doc_id}/preview")
def doc_preview(doc_id: int, db: Session = Depends(get_db)):
    rows = db.execute(text("select w.word, o.context, o.sentence, o.position from words w join word_occurrences o on o.word_id=w.id where o.document_id=:doc order by o.position"), {"doc": doc_id}).mappings().all()
    return ok({"id": doc_id, "blocks": [dict(row) for row in rows]})

@router.delete("/doc/{doc_id}")
def delete_doc(doc_id: int, db: Session = Depends(get_db)):
    document = db.get(Document, doc_id)
    if document:
        document.status = "DELETED"
        db.commit()
    return ok({"id": doc_id, "status": "DELETED"})

@router.post("/word/search")
def word_search(payload: WordSearchRequest, db: Session = Depends(get_db)):
    rows = search_words(db, payload.query, payload.limit)
    return ok({"items": rank_word_results(payload.query, rows)})

@router.get("/word/{word}")
def word_detail(word: str, db: Session = Depends(get_db)):
    rows = search_words(db, word, 50)
    return ok({"word": word, "occurrences": rows, "forms": sorted({r.get("lemma") for r in rows if r.get("lemma")})})

@router.post("/ocr/task")
def create_ocr_task(payload: OcrCheckRequest, db: Session = Depends(get_db)):
    answers = [row[0] for row in db.execute(text("select w.word_lower from words w join word_occurrences o on o.word_id=w.id where o.document_id=:doc order by o.position"), {"doc": payload.document_id}).all()]
    task = create_ocr_result(db, payload.document_id, payload.recognized_text, answers)
    return ok({"task_id": task.id, "status": task.status, "result": task.result})

@router.post("/ocr/upload")
async def upload_ocr_image(document_id: int = Form(...), file: UploadFile = File(...), db: Session = Depends(get_db)):
    with NamedTemporaryFile(suffix=Path(file.filename or "source.jpg").suffix, delete=True) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp.flush()
        recognized_text = recognize_handwriting_placeholder(tmp.name)
    answers = [row[0] for row in db.execute(text("select w.word_lower from words w join word_occurrences o on o.word_id=w.id where o.document_id=:doc order by o.position"), {"doc": document_id}).all()]
    task = create_ocr_result(db, document_id, recognized_text, answers)
    return ok({"task_id": task.id, "status": task.status, "recognized_text": recognized_text, "result": task.result})

@router.get("/ocr/task/{task_id}")
def ocr_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    return ok(None if task is None else {"task_id": task.id, "status": task.status, "result": task.result})

@router.post("/audio/task")
def create_audio_task(db: Session = Depends(get_db)):
    task = Task(task_type="AUDIO_SCORE", status="PENDING", progress=0)
    db.add(task)
    db.commit()
    db.refresh(task)
    return ok({"task_id": task.id, "status": task.status})

@router.get("/audio/task/{task_id}")
def audio_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    return ok(None if task is None else {"task_id": task.id, "status": task.status, "result": task.result})

@router.get("/error-record/list")
def error_list(db: Session = Depends(get_db)):
    rows = db.execute(text("select id, error_type, user_answer, correct_answer, created_at from error_records order by created_at desc limit 100")).mappings().all()
    return ok({"items": [dict(row) for row in rows], "total": len(rows)})

@router.get("/task/{task_id}")
def task_detail(task_id: int, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    return ok(None if task is None else {"task_id": task.id, "status": task.status, "progress": task.progress, "result": task.result})

@router.get("/task/list")
def task_list(db: Session = Depends(get_db)):
    tasks = db.query(Task).order_by(Task.created_at.desc()).limit(100).all()
    return ok({"items": [{"task_id": t.id, "task_type": t.task_type, "status": t.status, "progress": t.progress, "result": t.result} for t in tasks], "total": len(tasks)})

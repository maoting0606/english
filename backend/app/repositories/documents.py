from sqlalchemy import or_, select
from sqlalchemy.orm import Session
from app.models.entities import Document, DocumentFile, ErrorRecord, Task, Word, WordOccurrence
from app.services.parser import WordItem

DEFAULT_USER_ID = None

def create_document_from_items(db: Session, title: str, source_type: str, items: list[WordItem], source_file: dict | None = None) -> Document:
    document = Document(user_id=DEFAULT_USER_ID, title=title, source_type=source_type, status="READY", word_count=len(items))
    db.add(document)
    db.flush()
    if source_file:
        db.add(DocumentFile(document_id=document.id, file_type="SOURCE", upload_status="UPLOADED", **source_file))
    for position, item in enumerate(items):
        word = db.scalar(select(Word).where(Word.word_lower == item.word.lower()))
        if word is None:
            word = Word(word=item.word, word_lower=item.word.lower(), lemma=item.word.lower())
            db.add(word)
            db.flush()
        db.add(WordOccurrence(word_id=word.id, document_id=document.id, paragraph_index=position, sentence=f"{item.word} {item.meaning}", context=item.meaning, position=position))
    task = Task(task_type="DOCUMENT_PARSE", business_id=document.id, status="SUCCESS", progress=100, result={"word_count": len(items)})
    db.add(task)
    db.commit()
    db.refresh(document)
    return document

def list_documents(db: Session) -> list[Document]:
    return list(db.scalars(select(Document).where(Document.deleted_at.is_(None)).order_by(Document.created_at.desc())).all())

def search_words(db: Session, query: str, limit: int = 20) -> list[dict]:
    q = query.lower().strip()
    rows = db.execute(
        select(Word, WordOccurrence, Document)
        .join(WordOccurrence, WordOccurrence.word_id == Word.id)
        .join(Document, Document.id == WordOccurrence.document_id)
        .where(or_(Word.word_lower == q, Word.word_lower.like(f"%{q}%"), Word.lemma.like(f"%{q}%"), WordOccurrence.context.like(f"%{query}%")))
        .limit(limit)
    ).all()
    return [{"word": w.word, "lemma": w.lemma, "document_id": d.id, "document_title": d.title, "context": o.context, "sentence": o.sentence, "position": o.position} for w, o, d in rows]

def create_ocr_result(db: Session, document_id: int, recognized_text: str, answers: list[str]) -> Task:
    recognized = [token.lower() for token in recognized_text.split()]
    results = []
    for index, answer in enumerate(answers):
        user_answer = recognized[index] if index < len(recognized) else ""
        status = "CORRECT" if user_answer == answer.lower() else "WRONG"
        results.append({"answer": answer, "user_answer": user_answer, "status": status})
        if status != "CORRECT":
            db.add(ErrorRecord(document_id=document_id, error_type="OCR", user_answer=user_answer, correct_answer=answer))
    task = Task(task_type="OCR_CHECK", business_id=document_id, status="SUCCESS", progress=100, result={"items": results})
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_document_word_items(db: Session, document_id: int) -> list[WordItem]:
    rows = db.execute(
        select(Word.word, WordOccurrence.context)
        .join(WordOccurrence, WordOccurrence.word_id == Word.id)
        .where(WordOccurrence.document_id == document_id)
        .order_by(WordOccurrence.position)
    ).all()
    return [WordItem(word=word, meaning=context or "") for word, context in rows]

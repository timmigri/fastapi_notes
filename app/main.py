from typing import List

from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.orm import Session
from loguru import logger

from .database import engine, get_db
from .models import Base, Note
from .schemas import NoteCreate, NoteResponse
from .logger import setup_logger

setup_logger()
app = FastAPI()
Base.metadata.create_all(bind=engine)


@app.get("/health")
def health_check():
    logger.info("Health check passed")
    return {"status": "OK"}

@app.post("/notes", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
def create_note(note: NoteCreate, db: Session = Depends(get_db)):
    try:
        logger.info(f"Creating note: {note.dict()}")
        db_note = Note(**note.dict())
        db.add(db_note)
        db.commit()
        db.refresh(db_note)
        logger.success(f"Note created with ID: {db_note.id}")
        return db_note
    except Exception as e:
        logger.error(f"Error creating note: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/notes", response_model=List[NoteResponse])
def read_all_notes(db: Session = Depends(get_db)):
    logger.info(f"Fetching all notes")
    notes = db.query(Note).all()
    logger.debug(f"Found {len(notes)} notes")
    return notes

@app.get("/notes/{note_id}", response_model=NoteResponse)
def read_note(note_id: int, db: Session = Depends(get_db)):
    logger.info(f"Fetching note with ID: {note_id}")
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        logger.warning(f"Note {note_id} not found")
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@app.put("/notes/{note_id}", response_model=NoteResponse)
def update_note(note_id: int, note: NoteCreate, db: Session = Depends(get_db)):
    logger.info(f"Updating note {note_id} with data: {note.dict()}")
    db_note = db.query(Note).filter(Note.id == note_id).first()
    if not db_note:
        logger.warning(f"Note {note_id} not found for update")
        raise HTTPException(status_code=404, detail="Note not found")
    
    for key, value in note.dict().items():
        setattr(db_note, key, value)
    db.commit()
    logger.success(f"Note {note_id} updated successfully")
    return db_note

@app.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int, db: Session = Depends(get_db)):
    logger.info(f"Deleting note with ID: {note_id}")
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        logger.warning(f"Note {note_id} not found for deletion")
        raise HTTPException(status_code=404, detail="Note not found")
    
    db.delete(note)
    db.commit()
    logger.success(f"Note {note_id} deleted successfully")
    return {"detail": "Note deleted"}